import type { AICensorResponse } from '$types/ai';
import type { GraphNode } from '$types/pocketBase/TableTypes';
import { createNode } from '../nodes';
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
		events.qg.title,
		events.qg.text,
		events.qg.author,
		sessionId,
		String(triggerNode.id), // parent
		'event', // type
		qgSide ? qgSide.id : '' // side
	);
	await createNode(
		pb,
		events.terrain.title,
		events.terrain.text,
		events.terrain.author,
		sessionId,
		String(triggerNode.id),
		'event',
		terrainSide ? terrainSide.id : ''
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
