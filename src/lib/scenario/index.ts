import { scenarioSchema, fullScenarioSchema, nodeSchema } from '$lib/zschemas/scenario.schema';
import type { MyPocketBase } from '$types/pocketBase';
import type { z } from 'zod';

export async function getScenario(pb: MyPocketBase, scenarioId: string) {
	return await pb.collection('Scenario').getOne(scenarioId);
}

export async function createScenario(
	pb: MyPocketBase,
	scenarioData: z.infer<typeof scenarioSchema>,
	firstNodeData: z.infer<typeof nodeSchema>
) {
	const firstNode = {
		firstNodeTitle: firstNodeData.title,
		firstNodeText: firstNodeData.text,
		firstNodeAuthor: firstNodeData.author
	};
	return await pb.collection('scenario').create({ ...scenarioData, ...firstNode });
}

export async function createEventsAndEnds(
	pb: MyPocketBase,
	scenarioId: string,
	events: z.infer<typeof fullScenarioSchema>['events'],
	ends: z.infer<typeof fullScenarioSchema>['ends']
) {
	const eventPromises = events.map((event) =>
		pb.collection('event').create(
			{
				...event,
				scenario: scenarioId
			},
			{ requestKey: null } // Auto cancel See https://github.com/pocketbase/js-sdk#auto-cancellation
		)
	);

	const endPromises = ends.map((end) =>
		pb.collection('end').create(
			{
				...end,
				scenario: scenarioId
			},
			{ requestKey: null }
		)
	);

	return await Promise.all([...eventPromises, ...endPromises]);
}
