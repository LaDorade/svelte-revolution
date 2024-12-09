import { createSession } from '$lib/server/sessions';
import { createStartNode } from '$lib/server/nodes';
import { getScenario } from '$lib/server/scenario';
import { type Actions, fail } from '@sveltejs/kit';
import type { MyPocketBase } from '$types/pocketBase';
import { get } from 'svelte/store';
import { t } from 'svelte-i18n';
import { createSessionSchema } from '$lib/zschemas/createSession.schema.js';

export const actions = {
	createSession: async ({ request, locals }) => {
		const pb = locals.pb as MyPocketBase;
		if (!pb || !pb.authStore) {
			return fail(500, { error: get(t)('errors.internalError') });
		} else if (!pb.authStore.isValid || !pb.authStore.model || !pb.authStore.model.admin) {
			return fail(401, { error: get(t)('errors.unauthorized') });
		}

		const data = await request.formData();

		const formData = {
			name: data.get('name'),
			scenarioId: data.get('scenarioId'),
			image: data.get('image') as File
		};

		const sessionCreationValidation = createSessionSchema.safeParse(formData);
		if (!sessionCreationValidation.success) {
			return fail(400, {
				error: sessionCreationValidation.error.format()
			});
		}

		try {
			const scenario = await getScenario(pb, sessionCreationValidation.data.scenarioId.toString());
			if (!scenario) {
				return fail(404, { error: get(t)('errors.scenario.notFound') });
			}

			const session = await createSession(
				pb,
				sessionCreationValidation.data.name,
				scenario.id,
				pb.authStore.model.id,
				sessionCreationValidation.data.image
			);
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
