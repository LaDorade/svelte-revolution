import { createNode } from '$lib/server/nodes';
import { censorNode } from '$lib/server/ia';
import { createNewEvents, triggerEnd } from '$lib/server/ia/event';
import { type Actions, fail } from '@sveltejs/kit';
import type { GraphNode } from '$types/pocketBase/TableTypes';
import type { ClientResponseError } from 'pocketbase';
import { addNodeSchema } from '$lib/zschemas/addNode.schema';

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

		const validation = addNodeSchema.safeParse(nodeData);
		if (!validation.success) {
			return fail(422, { success: false, error: validation.error.format() });
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
			'contribution',
			nodeData.side
		);

		if (censorResponse.triggerEvent && censorResponse.events) {
			try {
				await createNewEvents(locals.pb, nodeData.session, censorResponse.events, node);
			} catch (e) {
				// TODO: Handle error
				console.log(e);
			}
		}

		if (censorResponse.triggerEnd) {
			try {
				await triggerEnd(locals.pb, nodeData.session, censorResponse.triggerEnd);
			} catch (e) {
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
				'event',
				null
			);
			await locals.pb.collection('Session').update(sessionId, { events: eventId });
		} catch (error) {
			const e = error as ClientResponseError;
			console.error('Error creating event:', e.toJSON());
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
