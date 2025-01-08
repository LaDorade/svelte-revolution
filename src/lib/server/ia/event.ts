import type { AICensorResponse } from '$types/ai';
import type { GraphNode } from '$types/pocketBase/TableTypes';
import { createNode } from '../nodes';
import { authIA } from './auth';

/**
 * Create new events if a response is good according to the AI
 */
export async function createNewEvents(sessionId: string, event: AICensorResponse['events'], triggerNode: GraphNode) {
	const pb = await authIA();
	if (!event || !pb) return;

	const scenario = await pb.collection('Scenario').getOne(sessionId);
	const sides = await pb
		.collection('Side')
		.getFullList({ filter: pb.filter('scenario = {:scenario}', { scenario: scenario.id }) });

	// TODO: Map the sides to the correct side, making it accessible to create
	const qgSide = sides.find((side) => side.name === 'QG');
	const terrainSide = sides.find((side) => side.name === 'Terrain');

	const qg = createNode(
		pb,
		event.qg.title,
		event.qg.text,
		event.qg.author,
		sessionId,
		String(triggerNode.id), // parent
		'event', // type
		qgSide ? qgSide.id : '' // side
	);
	const terrain = createNode(
		pb,
		event.terrain.title,
		event.terrain.text,
		event.terrain.author,
		sessionId,
		String(triggerNode.id),
		'event',
		terrainSide ? terrainSide.id : ''
	);
	return Promise.all([qg, terrain]);
}

export async function triggerEnd(sessionId: string, endId: string) {
	const pb = await authIA();
	if (!pb) {
		console.error('No pb');
		return;
	}

	await pb.collection('Session').update(sessionId, {
		completed: true,
		end: endId
	});
}
