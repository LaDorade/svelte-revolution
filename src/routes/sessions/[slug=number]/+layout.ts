import { getSession } from '$lib/sessions';
import { pb } from '$lib/client/pocketbase';
import { error, type ServerLoad } from '@sveltejs/kit';

import type { Session } from '$types/pocketBase/TableTypes';
import type { AdminInfo } from '$stores/session.svelte';

export const load: ServerLoad = async ({ params }) => {
	const session = await getSession(Number(params.slug));
	const scenario = session.expand?.scenario || null;
	if (!scenario) {
		error(500, {
			status: 500,
			message: 'No scenario for session'
		});
	}

	const sides = await getSides(session.scenario);

	// AI is now run by the Python ia_server which subscribes to PocketBase
	// directly. There is no per-request health check from the frontend — we
	// surface "connected" as soon as the scenario has AI enabled.
	const aiConnected = !!session.expand?.scenario?.ai;

	const nodes = pb
		.collection('Node')
		.getFullList({ filter: pb.filter('session = {:session}', { session: session.id }), expand: 'side' });

	return {
		ai: {
			connected: aiConnected
		},
		admin: {
			...await adminCheck(session),
		},
		session,
		scenario,
		sides,
		nodesPromise: nodes,
	};
};

async function adminCheck(sessionData: Session): Promise<AdminInfo> {
	if (sessionData.author === pb.authStore.record?.id || pb.authStore.record?.role === 'superAdmin') {
		if (pb.authStore.isValid) {
			const scenario = sessionData.scenario;
			return {
				isAdmin: true,
				events: await pb.collection('Event').getFullList({
					filter: pb.filter('scenario = {:scenario}', { scenario })
				}),
				ends: await pb.collection('End').getFullList({
					filter: pb.filter('scenario = {:scenario}', { scenario })
				}),
			};
		}
	}
	return {
		isAdmin: false,
		events: null,
		ends: null
	};
}

async function getSides(scenarioId: string) {
	const sidesFromDb = await pb.collection('Side').getFullList({
		filter: pb.filter('scenario = {:scenario}', { scenario: scenarioId })
	});
	const sides = sidesFromDb.map((side, i) => {
		return {
			id: side.id,
			name: side.name,
			number: i
		};
	});
	return sides;
}
