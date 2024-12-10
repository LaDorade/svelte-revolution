import type { AICensorResponse } from '$types/ai';
import { createNode } from '../nodes';
import { authIA } from './auth';

export async function createNewEvents(sessionId: string, event: AICensorResponse['events']) {
	const pb = await authIA();
	if (!event || !pb) return;

	const scenario = await pb.collection('Scenario').getOne(sessionId);
	const parent = await pb
		.collection('Node')
		.getFirstListItem(
			pb.filter('type = {:type} && session = {:session}', { session: sessionId, type: 'startNode' })
		);
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
		String(parent?.id) || '',
		qgSide ? qgSide.id : '',
		'event'
	);
	const terrain = createNode(
		pb,
		event.terrain.title,
		event.terrain.text,
		event.terrain.author,
		sessionId,
		String(parent?.id) || '',
		terrainSide ? terrainSide.id : '',
		'event'
	);
	return Promise.all([qg, terrain]);
}
