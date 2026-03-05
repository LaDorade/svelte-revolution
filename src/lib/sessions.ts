import { error } from '@sveltejs/kit';
import { ClientResponseError } from 'pocketbase';
import type { Session } from '$types/pocketBase/TableTypes';
import { pb } from '$lib/client/pocketbase';
import type { LinkMessage } from '$types/graph';
import type { GraphNode } from '$types/pocketBase/TableTypes';

export function buildLinks(nodes: GraphNode[]) {
	const links: LinkMessage[] = [];

	for (const node of nodes) {
		const parent = nodes.find((n) => n.id === node.parent);
		if (parent) {
			links.push({
				source: parent,
				target: node
			});
		}
	}

	return links;
}

export async function getSession(sessionId: number) {
	let session: Session;
	try {
		session = await pb
			.collection('session')
			.getFirstListItem('slug=' + sessionId.toString(), { expand: 'end, scenario, events' });
	} catch (e) {
		const err = e as ClientResponseError;
		if (err.status === 404) {
			error(404, {
				status: 404,
				message: 'Session not found'
			});
		} else {
			error(500, {
				status: err.status,
				message: err.message
			});
		}
	}

	return session;
}

export async function createSession(
	name: FormDataEntryValue,
	scenarioId: string,
	author: FormDataEntryValue,
	image: File | null | undefined
) {
	const scenario = await pb.collection('Scenario').getOne(scenarioId);
	const sessions = await pb.collection('Session').getFullList({ fields: 'id, slug' });

	const session = await pb.collection('Session').create({
		name,
		scenario: scenarioId,
		author,
		slug: Math.max(...sessions.map(s => s.slug || 0)) + 1,
		public: true,
		visible: true,
		completed: false,
		image
	});

	if (scenario.ai) {
		const cookies = pb.authStore.exportToCookie();
		const result = await fetch('/api/ai/newAiSession', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ sessionId: session.id, scenarioId, cookies })
		});
		if (!result.ok) {
			console.error('Error creating AI session:', result);
		}
	}

	return session;
}
