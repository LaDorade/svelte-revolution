import { getSession } from '$lib/server/sessions';
import { createNode } from '$lib/server/nodes';
import { apiHealthy, censorNode } from '$lib/server/ia';
import { createNewEvents } from '$lib/server/ia/event';
import { type Actions, fail, type ServerLoad } from '@sveltejs/kit';
import type { End, GraphEvent, GraphNode, Session } from '$types/pocketBase/TableTypes';
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

export const actions: Actions = {
	addNode: async ({ request, locals }) => {
		const data = await request.formData();

		let nodeData = {
			title: data.get('title') as string,
			text: data.get('text') as string,
			author: data.get('author') as string,
			parent: data.get('parent') as string,
			session: data.get('session') as string,
			side: data.get('side') as string
		};

		if (!nodeData.parent) {
			return fail(422, { success: false, error: 'No selected node' });
		}
		if (!nodeData.session) {
			return fail(500, { success: false, error: 'Not in a session' });
		}
		if (!nodeData.title || !nodeData.text || !nodeData.author || !nodeData.side) {
			return fail(422, { success: false, error: 'Missing required fields' });
		}

		const censorResponse = await censorNode(nodeData);
		nodeData = censorResponse.node;

		const node = await createNode(
			locals.pb,
			nodeData.title,
			nodeData.text,
			nodeData.author,
			nodeData.session,
			nodeData.parent,
			nodeData.side,
			'contribution'
		);

		if (censorResponse.triggerEvent && censorResponse.events) {
			try {
				await createNewEvents(nodeData.session, censorResponse.events);
			} catch (e) {
				// TODO: Handle error
				console.log(e);
			}
		}

		return {
			status: 200,
			success: true,
			body: { message: 'Node added', node: JSON.stringify(node) }
		};
	},
	// Admin only
	addEvent: async ({ request, locals }) => {
		const data = await request.formData();
		const eventId = data.get('eventId') as string;
		const sessionId = data.get('session') as string;

		// check if user is superAdmin or author
		if (locals.pb.authStore.model?.role !== 'superAdmin') {
			const session = await locals.pb.collection('Session').getOne(sessionId, { fields: 'author' });
			if (session.author !== locals.pb.authStore.model?.id) {
				return fail(401, { success: false, error: 'Unauthorized' });
			}
		}

		if (!sessionId) {
			return fail(500, { success: false, error: 'Not in a session' });
		}
		if (!eventId) {
			return fail(422, { success: false, error: 'Missing event field' });
		}

		let createdEventNode: GraphNode | null = null;
		try {
			const { title, text, author } = await locals.pb.collection('Event').getOne(eventId);
			const firstNode = await locals.pb.collection('Node').getFirstListItem(
				locals.pb.filter('type = {:type} && session = {:session}', {
					session: sessionId,
					type: 'startNode'
				})
			);
			createdEventNode = await createNode(
				locals.pb,
				title,
				text,
				author,
				sessionId,
				String(firstNode.id),
				'event'
			);
			await locals.pb.collection('Session').update(sessionId, { events: eventId });
		} catch (error) {
			console.error('Error creating event:', JSON.stringify(error));
			if (createdEventNode) {
				await locals.pb.collection('Node').delete(String(createdEventNode.id));
			}
			return fail(500, { success: false, error: 'Error while creating event' });
		}

		return {
			status: 200,
			success: true,
			body: { message: 'Event added', event: createdEventNode }
		};
	},
	endSession: async ({ request, locals }) => {
		const data = await request.formData();
		const sessionId = data.get('session') as string;
		const endId = data.get('endId') as string;

		// check if user is superAdmin or author
		if (locals.pb.authStore.model?.role !== 'superAdmin') {
			const session = await locals.pb.collection('Session').getOne(sessionId, { fields: 'author' });
			if (session.author !== locals.pb.authStore.model?.id) {
				return fail(401, { success: false, error: 'Unauthorized' });
			}
		}

		if (!sessionId) {
			return fail(500, { success: false, error: 'Not in a session' });
		}
		if (!endId) {
			return fail(422, { success: false, error: 'Missing required fields' });
		}

		try {
			await locals.pb.collection('Session').update(sessionId, {
				completed: true,
				end: endId
			});
		} catch (error) {
			console.error('Error ending session:', JSON.stringify(error));
			return fail(500, { success: false, error: 'Error while ending session' });
		}

		return {
			status: 200,
			success: true,
			body: { message: 'Session ended' }
		};
	}
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
