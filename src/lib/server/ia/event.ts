import type { AICensorResponse } from '$types/ai';
import type { GraphNode } from '$types/pocketBase/TableTypes';
import { createNode } from '../../nodes';
import { type MyPocketBase } from '../../../types/pocketBase/index';

/**
 * Create new events if a response is good according to the AI
 */
export async function createNewEvents(
	pb: MyPocketBase,
	sessionId: string,
	events: AICensorResponse['events'],
	triggerNode: GraphNode
) {
	if (!events || !pb) return;

	const scenario = (await pb.collection('Session').getOne(sessionId, { expand: 'scenario' })).expand?.scenario;
	const sides = await pb
		.collection('Side')
		.getFullList({ filter: pb.filter('scenario = {:scenario}', { scenario: scenario?.id }) });

	// TODO: Map the sides to the correct side, making it accessible to create
	const qgSide = sides.find((side) => side.name.toLocaleLowerCase() === 'qg');
	const terrainSide = sides.find((side) => side.name.toLocaleLowerCase() === 'terrain');

	await createNode(
		pb,
		{
			title: events.qg.title,
			text: events.qg.text,
			author: events.qg.author,
			session: sessionId,
			parent: String(triggerNode.id), // parent
			type: 'event', // type
			side: qgSide ? qgSide.id : '' // side
		}
	);
	await createNode(
		pb,
		{
			title: events.terrain.title,
			text: events.terrain.text,
			author: events.terrain.author,
			session: sessionId,
			parent: String(triggerNode.id),
			type: 'event',
			side: terrainSide ? terrainSide.id : ''
		}
	);
}

export async function triggerEnd(pb: MyPocketBase, sessionId: string, endId: string) {
	if (!pb) {
		console.error('No pb');
		return;
	}

	await pb.collection('Session').update(sessionId, {
		completed: true,
		end: endId
	});
}
