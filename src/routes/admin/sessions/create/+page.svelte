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
	import Input from '$components/form/Input.svelte';
	import Base from '$components/form/Base.svelte';
	import Button from '$components/Button.svelte';
	import Select from '$components/form/Select.svelte';

	let { data } = $props();

	let form = $state({
		name: '',
		scenarioId: '',
		image: null as FileList | null,
		useAudio: false
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
			const session = await createSession({
				name: form.name,
				scenario: form.scenarioId,
				author: pb.authStore.record.id,
				image: image as unknown as string, // we upload a file but we receive a string (url)
				useAudio: form.useAudio
			});
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
			<Input
				label={$t('admin.session.name')}
				placeholder="Votre nouvelle session"
				bind:value={form.name}
				required
			/>
			<Base>
				{#snippet label()}
					<div class="">
						{$t('admin.session.image')}
						<span class="text-xs text-gray-400 lowercase">
							({$t('form.notRequired')})
						</span>
					</div>
				{/snippet}
				<input
					bind:files={form.image}
					type="file"
					name="image"
					accept="image/*"
					class="appearance-none text-sm font-light text-gray-500 w-full flex justify-between"
				/>
			</Base>
			{#if form.image && form.image.item(0)}
				<div class="flex flex-col gap-4 p-4 items-center">
					<img src={URL.createObjectURL(form.image.item(0) as Blob)} alt="preview" class="w-1/2" />
				</div>
			{/if}
			<Select
				triggerClass="w-full"
				label={$t('admin.session.selectScenario')}
				values={data.scenarios.map((s) => ({ 
					value: s.id,
					label: s.title,
					group: s.ai ? $t('admin.session.aiScenarios') : $t('scenario.scenarios')
				}))}
				groups={[$t('scenario.scenarios'), $t('admin.session.aiScenarios')]}
				bind:value={form.scenarioId}
			/>
			<Base 
				label={$t('admin.session.authorizeAudio')}
				labelClass="w-full flex-row items-center justify-between"
			>
				<input type="checkbox" bind:checked={form.useAudio} />
			</Base>
			<Button
				type="submit"
				variant="primary"
				onclick={createNewSession}
				disabled={!validForm}
			>
				{$t('admin.session.createTheSession')}
			</Button>
		</div>
	</div>
</div>
