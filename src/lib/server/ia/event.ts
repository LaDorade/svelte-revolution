import type { AICensorResponse } from '$types/ai';
import { authIA } from './auth';

export async function createNewEvents(sessionId: string, event: AICensorResponse['events']) {
	const pb = await authIA();
	if (!event || !pb) return;

	const scenario = await pb.collection('Scenario').getOne(sessionId);
	const sides = await pb
		.collection('Side')
		.getFullList({ filter: pb.filter('scenario = {:scenario}', { scenario: scenario.id }) });

	const qgSide = sides.find((side) => side.name === 'QG');
	const terrainSide = sides.find((side) => side.name === 'Terrain');

	const side1 = pb.collection('Node').create({
		title: event.qg.title,
		text: event.qg.text,
		author: event.qg.author,
		session: sessionId,
		type: 'event',
		side: qgSide?.id || ''
	});
	const side2 = pb.collection('Node').create({
		title: event.terrain.title,
		text: event.terrain.text,
		author: event.terrain.author,
		session: sessionId,
		type: 'event',
		side: terrainSide?.id || ''
	});
	return Promise.all([side1, side2]);
}
