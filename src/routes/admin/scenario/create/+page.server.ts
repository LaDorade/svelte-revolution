import { fail, type Actions } from '@sveltejs/kit';
import { createEventsAndEnds, createScenario } from '$lib/scenario';
import { fullScenarioSchema } from '$lib/zschemas/scenario.schema';
import { aiConfigSchema } from '$lib/zschemas/aiConfig.schema';
import { z } from 'zod';
import PocketBase from 'pocketbase';
import { env } from '$env/dynamic/private';
const DB_URL = env.DB_URL;

// TODO: Refacto to use zod schema, errors and translations
export const actions = {
	createScenario: async ({ request }) => {
		const data = await request.formData();

		const pb = new PocketBase(DB_URL);
		const pb_cookie = data.get('pb_cookie') as string;
		pb.authStore.loadFromCookie(pb_cookie);

		await pb.collection('users').authRefresh();
		
		if (!pb || !pb.authStore) {
			return fail(500, { error: 'Database not connected' });
		} else if (!pb.authStore.isValid || !pb.authStore.record) {
			// TODO better auth check
			return fail(401, { error: 'Unauthorized' });
		}

		// TODO : gérer ça dans pocketbase

		const { scenarioData, firstNode, sides, events, ends } = parseFormData(data);

		try {
			const parsed = fullScenarioSchema.parse({
				...scenarioData,
				firstNode,
				sides,
				events,
				ends
			});

			if (parsed.ai && parsed.aiConfig) {
				try {
					aiConfigSchema.parse(JSON.parse(parsed.aiConfig));
				} catch {
					return fail(400, { error: 'Invalid AI configuration' });
				}
			}

			try {
				const scenarioInDb = {
					title: parsed.title,
					prologue: parsed.prologue,
					lang: parsed.lang,
					ai: parsed.ai,
					aiConfig: parsed.aiConfig
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
						await Promise.all(parsed.sides.map(async (side) => {
							return pb
								.collection('Side')
								.create({
									scenario: scenario.id,
									name: side.title
								}, { requestKey: null });
						})).catch((e) => console.error(e));
					} catch (err) {
						console.error(err);
						await pb.collection('Scenario').delete(scenario.id);
						return fail(500, { error: 'Fail creating sides' });
					}
				} catch {
					await pb.collection('Scenario').delete(scenario.id);
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
			console.error(z.treeifyError(err));
			return fail(400, { error: message, path });
		}
	}
} satisfies Actions;

function parseFormData(data: FormData) {
	const aiConfigRaw = data.get('aiConfig')?.toString() || undefined;
	const scenarioData = {
		title: data.get('title')?.toString(),
		prologue: data.get('prologue')?.toString(),
		lang: data.get('lang')?.toString(),
		ai: Boolean(data.get('useAi')),
		aiConfig: aiConfigRaw
	};

	const events = data.getAll('eventTitle').map((title, index) => ({
		title: title.toString(),
		text: data.getAll('eventText')[index]?.toString() || '',
		author: data.getAll('eventAuthor')[index]?.toString() || ''
	}));

	const sides = data.getAll('side').map((side) => ({
		title: side.toString()
	}));

	const ends = data.getAll('endTitle').map((title, index) => ({
		title: title.toString(),
		text: data.getAll('endText')[index]?.toString() || ''
	}));

	const firstNode = {
		title: data.get('firstNodeTitle')?.toString(),
		text: data.get('firstNodeText')?.toString(),
		author: data.get('firstNodeAuthor')?.toString()
	};

	return { scenarioData, firstNode, sides, events, ends };
}
