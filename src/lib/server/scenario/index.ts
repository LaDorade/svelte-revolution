import type { MyPocketBase } from '$types/pocketBase';

export async function getScenario(pb: MyPocketBase, scenarioId: string) {
	return await pb.collection('Scenario').getOne(scenarioId);
}

export async function createScenario(
	pb: MyPocketBase,
	data: {
		title: FormDataEntryValue;
		prologue: FormDataEntryValue;
		lang: FormDataEntryValue;
		firstNodeTitle: FormDataEntryValue;
		firstNodeText: FormDataEntryValue;
		firstNodeAuthor: FormDataEntryValue;
	}
) {
	return pb.collection('scenario').create(data);
}

export async function createEventsAndEnds(
	pb: MyPocketBase,
	scenarioId: string,
	events: FormDataEntryValue[],
	eventTexts: FormDataEntryValue[],
	eventAuthors: FormDataEntryValue[],
	ends: FormDataEntryValue[],
	endTexts: FormDataEntryValue[]
) {
	const eventPromises = events.map((event, i) =>
		pb.collection('event').create(
			{
				title: event,
				text: eventTexts[i],
				author: eventAuthors[i],
				scenario: scenarioId
			},
			{ requestKey: null } // Auto cancel See https://github.com/pocketbase/js-sdk#auto-cancellation
		)
	);

	const endPromises = ends.map((end, i) =>
		pb.collection('end').create(
			{
				title: end,
				text: endTexts[i],
				scenario: scenarioId
			},
			{ requestKey: null }
		)
	);

	return await Promise.all([...eventPromises, ...endPromises]);
}
