import { getSession } from '$lib/server/sessions';
import { apiHealthy } from '$lib/server/ia';
import { type ServerLoad } from '@sveltejs/kit';
import type { End, GraphEvent, Session } from '$types/pocketBase/TableTypes';
import type { MyPocketBase } from '$types/pocketBase';

export const load: ServerLoad = async ({ params, locals }) => {
	const pb = locals.pb;
	const sessionData = await getSession(pb, Number(params.slug));

	const { events, ends } = await adminCheck(pb, sessionData);

	const sides = await getSides(sessionData.scenario, pb);

	// ? Check if AI server is connected and if the scenario has IA
	const iaConnected = (await apiHealthy()) && sessionData.expand?.scenario?.ai;

	const nodes = pb
		.collection('Node')
		.getFullList({ filter: pb.filter('session = {:session}', { session: sessionData.id }), expand: 'side' });

	return {
		iaConnected,
		sessionData,
		scenario: sessionData.expand?.scenario,
		nodesPromise: nodes,
		events,
		ends,
		sides,
		isAdmin:
			sessionData.author === locals.pb.authStore.model?.id || locals.pb.authStore.model?.role === 'superAdmin'
	};
};

async function adminCheck(pb: MyPocketBase, sessionData: Session) {
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

async function getSides(scenarioId: string, pb: MyPocketBase) {
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
