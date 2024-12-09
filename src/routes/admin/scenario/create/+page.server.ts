import { fail, type Actions } from '@sveltejs/kit';
import { createEventsAndEnds, createScenario } from '$lib/server/scenario';
import { fullScenarioSchema } from '$lib/zschemas/scenario.schema';
import type { MyPocketBase } from '$types/pocketBase';
import type { z } from 'zod';

// TODO: Refacto to use zod schema, errors and translations
export const actions = {
	createScenario: async ({ request, locals }) => {
		const pb = locals.pb as MyPocketBase;
		if (!pb || !pb.authStore) {
			return fail(500, { error: 'Database not connected' });
		} else if (!pb.authStore.isValid || !pb.authStore.model) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();

		const { scnearioData, firstNode, sides, events, ends } = parseFormData(data);

		try {
			const parsed = fullScenarioSchema.parse({
				...scnearioData,
				firstNode,
				sides,
				events,
				ends
			});
			try {
				const scenarioInDb = {
					title: parsed.title,
					prologue: parsed.prologue,
					lang: parsed.lang,
					ai: parsed.ai
				};
				const firstNodeInDb = {
					title: parsed.firstNode.title,
					text: parsed.firstNode.text,
					author: parsed.firstNode.author
				};
				const scenario = await createScenario(pb, scenarioInDb, firstNodeInDb);

				try {
					await createEventsAndEnds(pb, scenario.id, events, ends);
					try {
						parsed.sides.forEach(async (side) => {
							await pb
								.collection('Side')
								.create({ scenario: scenario.id, name: side.title }, { requestKey: null });
						});
					} catch {
						pb.collection('scenario').delete(scenario.id);
						return fail(500, { error: 'Fail creating sides' });
					}
				} catch {
					pb.collection('scenario').delete(scenario.id);
					return fail(500, { error: 'Fail creating events and ends' });
				}

				return {
					success: true,
					status: 201,
					body: scenario
				};
			} catch {
				return fail(500, { error: 'Fail creating scenario' });
			}
		} catch (error) {
			const err = error as z.ZodError;
			const { message, path } = err.issues[0];
			console.log(err.format());
			return fail(400, { error: message, path });
		}
	}
} satisfies Actions;

function parseFormData(data: FormData) {
	const scnearioData = {
		title: data.get('title')?.toString(),
		prologue: data.get('prologue')?.toString(),
		lang: data.get('lang')?.toString(),
		ai: data.get('useAi')?.toString(),
		bannedWords: data.getAll('bannedWords').map((word) => word.toString())
	};
	const events: z.infer<typeof fullScenarioSchema>['events'] = data.getAll('endTitle').map((endTitle, index) => {
		return {
			title: endTitle.toString(),
			text: data.getAll('eventText')[index].toString(),
			author: data.getAll('eventAuthor')[index].toString()
		};
	});
	const sides: z.infer<typeof fullScenarioSchema>['sides'] = data.getAll('side').map((side) => {
		return {
			title: side.toString()
		};
	});
	const ends: z.infer<typeof fullScenarioSchema>['ends'] = data.getAll('endTitle').map((endTitle, index) => {
		return {
			title: endTitle.toString(),
			text: data.getAll('endText')[index].toString()
		};
	});
	const firstNode = {
		title: data.get('firstNodeTitle')?.toString(),
		text: data.get('firstNodeText')?.toString(),
		author: data.get('firstNodeAuthor')?.toString()
	};
	return { scnearioData, firstNode, sides, events, ends };
}
