<script lang="ts">
	import { t } from 'svelte-i18n';
	import nProgress from 'nprogress';
	import { createSessionSchema } from '$lib/zschemas/createSession.schema';
	import { getScenario } from '$lib/scenario';
	import toast from 'svelte-french-toast';
	import { createSession } from '$lib/sessions';
	import { pb } from '$lib/client/pocketbase';
	import { createStartNode } from '$lib/nodes';
	import type { ClientResponseError } from 'pocketbase';

	let { data } = $props();

	let form = $state({
		name: '',
		scenarioId: '',
		image: null as FileList | null
	});

	const validForm = $derived.by(() => {
		return createSessionSchema.safeParse(form).success;
	});

	const createNewSession = async () => {
		nProgress.start();
		let errorMessage = '';

		try {
			const scenario = await getScenario(pb, form.scenarioId.toString());
			if (!scenario) {
				errorMessage = $t('errors.scenario.notFound');
				throw new Error(errorMessage);
			}
			if (!pb.authStore.record) {
				errorMessage = $t('errors.user.notFound');
				throw new Error(errorMessage);
			}

			const image = form.image?.item(0);
			const session = await createSession(form.name, scenario.id, pb.authStore.record?.id, image);
			await createStartNode(pb, scenario, session.id);

			toast.success($t('admin.session.creationSuccess'));
		} catch (error) {
			const err = error as ClientResponseError;
			console.log(err.toJSON());
			toast.error(errorMessage || err.message);
		} finally {
			nProgress.done();
		}
	};
</script>

<div class="flex flex-col items-center justify-center mx-4 text-gray-100">
	<div class="flex flex-col items-center p-4 shadow-xl rounded-xl bg-black/30">
		<h2 class="p-4 text-3xl font-bold">{$t('admin.session.createSession')}</h2>
		<div class="flex flex-col gap-4 p-4 text-center border-t shadow-md">
			<div class="flex flex-col gap-4">
				<label for={'name'} class="text-xl font-thin">{$t('admin.session.name')}</label>
				<input
					required
					bind:value={form.name}
					name={'name'}
					placeholder="Votre nouvelle session"
					class="w-full p-4 border-b placeholder:font-thin placeholder:italic focus:border-white"
				/>
			</div>
			<div class="flex flex-col gap-4 p-4">
				<label class="text-xl" for="image">{$t('admin.session.image')}</label>
				<input
					bind:files={form.image}
					type="file"
					name="image"
					accept="image/*"
					class="p-4 border-b appearance-none focus-within:bg-transparent"
				/>
			</div>
			{#if form.image && form.image.item(0)}
				<div class="flex flex-col gap-4 p-4 items-center">
					<img src={URL.createObjectURL(form.image.item(0) as Blob)} alt="preview" class="w-1/2" />
				</div>
			{/if}
			<div class="flex flex-col gap-4 p-4">
				<label class="text-xl" for="scenarioId">{$t('admin.session.selectScenario')}</label>
				<select
					name="scenarioId"
					class="p-4 border-b focus:ring-0 focus:border-white"
					bind:value={form.scenarioId}
					required
				>
					<option value="" disabled selected>{$t('admin.session.selectScenario')}</option>
					<optgroup label={$t('scenario.scenarios')}>
						{#each data.scenarios.filter((s) => !s.ai) as scenario}
							<option value={scenario.id}>{scenario.title}</option>
						{/each}
					</optgroup>
					<optgroup label={$t('admin.session.aiScenarios')}>
						{#each data.scenarios.filter((s) => s.ai) as scenario}
							<option value={scenario.id}>{scenario.title}</option>
						{/each}
					</optgroup>
				</select>
			</div>
			<button
				type="submit"
				onclick={createNewSession}
				disabled={!validForm}
				class="self-center px-4 py-2 text-lg text-black transition-all ease-linear bg-white rounded disabled:cursor-not-allowed disabled:opacity-50"
			>
				{$t('admin.session.createTheSession')}
			</button>
		</div>
	</div>
</div>
