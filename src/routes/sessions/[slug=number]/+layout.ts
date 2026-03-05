import { getSession } from '$lib/sessions';
import { pb } from '$lib/client/pocketbase';
import { type ServerLoad } from '@sveltejs/kit';
import type { End, GraphEvent, Session } from '$types/pocketBase/TableTypes';

export const load: ServerLoad = async ({ params, fetch }) => {
	const sessionData = await getSession(Number(params.slug));

	const { events, ends } = await adminCheck(sessionData);

	const sides = await getSides(sessionData.scenario);

	const aiHealty = await fetch('/api/ai/health', { method: 'POST' })
		.then((res) => res.json())
		.then((res) => res.aiHealthy);
	const aiConnected = aiHealty && sessionData.expand?.scenario?.ai;

	const nodes = pb
		.collection('Node')
		.getFullList({ filter: pb.filter('session = {:session}', { session: sessionData.id }), expand: 'side' });

	return {
		aiConnected,
		sessionData,
		scenario: sessionData.expand?.scenario,
		nodesPromise: nodes,
		events,
		ends,
		sides,
		isAdmin: sessionData.author === pb.authStore.model?.id || pb.authStore.model?.role === 'superAdmin'
	};
};

async function adminCheck(sessionData: Session) {
	let events: GraphEvent[] = [];
	let ends: End[] = [];
	if (sessionData.author === pb.authStore.model?.id || pb.authStore.model?.role === 'superAdmin') {
		if (pb.authStore.isValid) {
			const scenario = sessionData.scenario;
			events = await pb.collection('Event').getFullList({
				filter: pb.filter('scenario = {:scenario}', { scenario })
			});
			ends = await pb.collection('End').getFullList({
				filter: pb.filter('scenario = {:scenario}', { scenario })
			});
		}
	}
	return { events, ends };
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
