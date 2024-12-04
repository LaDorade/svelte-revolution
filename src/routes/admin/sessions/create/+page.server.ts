import { createSession } from '$lib/server/sessions';
import { createStartNode } from '$lib/server/nodes';
import { getScenario } from '$lib/server/scenario';
import { type Actions, fail } from '@sveltejs/kit';
import type { MyPocketBase } from '$types/pocketBase';

export const actions = {
	createSession: async ({ request, locals }) => {
		const pb = locals.pb as MyPocketBase;
		if (!pb || !pb.authStore) {
			return fail(500, { error: 'Database not connected' });
		} else if (!pb.authStore.isValid || !pb.authStore.model) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();

		const name = data.get('name');
		const scenarioId = data.get('scenarioId');
		const image = data.get('image') as File;

		if (!name || !scenarioId) {
			return fail(400, { error: 'Missing required fields' });
		}

		try {
			const scenario = await getScenario(pb, scenarioId.toString());
			if (!scenario) {
				return fail(404, { error: 'Scenario not found' });
			}

			const session = await createSession(pb, name, scenario.id, pb.authStore.model.id, image);
			await createStartNode(pb, scenario, session.id);

			if (scenario.ai) {
				// TODO Create AI session
			}

			return {
				status: 201,
				success: true,
				session: session
			};
		} catch (error) {
			return fail(500, {
				error: String(error)
			});
		}
	}
} satisfies Actions;

export const load = async ({ parent, locals }) => {
	const scenarios = await locals.pb.collection('scenario').getFullList();
	return {
		...(await parent()),
		scenarios
	};
};
