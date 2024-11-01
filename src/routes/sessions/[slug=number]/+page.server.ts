import { getSession } from '$lib/server/sessions';
import { createNode } from '$lib/server/sessions/create';
import { type Actions, fail, type ServerLoad } from '@sveltejs/kit';
import type { End, GraphEvent } from '$types/pocketBase/TableTypes';
import type { GraphNode } from '$types/pocketBase/TableTypes';
import { buildLinks } from '$lib/sessions';
import { env } from '$env/dynamic/private';

const iaserver = env.IA_SERVER_URL;
const checkMsgURL = iaserver ? `${iaserver}/api/checkMsg` : '';

export const load: ServerLoad = async ({ params, locals }) => {
	const pb = locals.pb;
	const sessionData = await getSession(pb, Number(params.slug));

	const nodes = await pb
		.collection('Node')
		.getFullList({ filter: pb.filter('session = {:session}', { session: sessionData.id }) });

	const links = buildLinks(nodes);

	// Admin only
	let events: GraphEvent[] = [];
	let ends: End[] = [];
	if (sessionData.author === locals.pb.authStore.model?.id || locals.pb.authStore.model?.role === 'superAdmin') {
		if (locals.pb.authStore.isValid) {
			const scenario = sessionData.expand?.scenario?.id;
			events = await locals.pb.collection('Event').getFullList({
				filter: locals.pb.filter('scenario = {:scenario}', { scenario })
			});
			ends = await locals.pb.collection('End').getFullList({
				filter: locals.pb.filter('scenario = {:scenario}', { scenario })
			});
		}
	}
	// ---

	const sides = await locals.pb.collection('Side').getFullList({
		filter: locals.pb.filter('scenario = {:scenario}', { scenario: sessionData?.expand?.scenario?.id })
	});

	let iaConnected = false;
	if (iaserver) {
		try {
			const response = await fetch(`${iaserver}/api/health`);
			if (response.ok) {
				iaConnected = true;
			}
		} catch (error) {
			console.error('IA Server not reachable');
		}
	}

	return {
		sessionData,
		nodesAndLinks: {
			nodes,
			links
		},
		events,
		ends,
		sides,
		// Admin onlys
		isAdmin:
			sessionData.author === locals.pb.authStore.model?.id || locals.pb.authStore.model?.role === 'superAdmin',
		iaConnected
	};
};

export const actions: Actions = {
	addNode: async ({ request, locals }) => {
		const data = await request.formData();

		const title = data.get('title') as string;
		const text = data.get('text') as string;
		const author = data.get('author') as string;
		const parent = data.get('parent') as string;
		const session = data.get('session') as string;
		const side = data.get('side') as string;

		if (!parent) {
			return fail(422, { success: false, error: 'No selected node' });
		}
		if (!session) {
			return fail(500, { success: false, error: 'Not in a session' });
		}
		if (!title || !text || !author || !side) {
			return fail(422, { success: false, error: 'Missing required fields' });
		}

		const nodeData = { title, text, author, parent, session, side };

		// TODO: ajouter ici le check ia si besoin
		if (iaserver) {
			try {
				const response = await fetch(checkMsgURL, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(nodeData)
				});
				if (response.ok) {
					const result = await response.json();
					nodeData.text = result.text;
					nodeData.title = result.title;
				}
			} catch (error) {
				console.error('IA Server not reachable', error);
			}
		}

		const node = await locals.pb.collection('Node').create({
			...nodeData,
			type: 'contribution'
		});

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
			return fail(422, { success: false, error: 'Missing required fields' });
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
			createdEventNode = await createNode(locals.pb, title, text, author, sessionId, firstNode, 'event');
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
