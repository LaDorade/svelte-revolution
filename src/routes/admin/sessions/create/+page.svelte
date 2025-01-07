<script lang="ts">
	import { enhance } from '$app/forms';
	import { t } from 'svelte-i18n';
	import toast from 'svelte-french-toast';
	import nProgress from 'nprogress';
	import type { ActionData, PageData } from './$types';

	interface Props {
		form: ActionData;
		data: PageData;
	}
	let { form, data }: Props = $props();

	let theForm: HTMLFormElement;
	let validForm = $state(false);

	$effect(() => {
		if (form?.success) {
			toast.success($t('admin.session.creationSuccess'), { duration: 5000, position: 'bottom-center' });
		}
	});
</script>

<div class="flex flex-col items-center">
	<h1 class="p-4 text-3xl font-bold">{$t('admin.session.createSession')}</h1>
	<form
		action="?/createSession"
		method="POST"
		enctype="multipart/form-data"
		bind:this={theForm}
		oninput={() => (validForm = theForm?.checkValidity())}
		use:enhance={() => {
			nProgress.start();
			return async ({ update }) => {
				await update();
				nProgress.done();
			};
		}}
		class="flex flex-col gap-4 p-4 text-center border-t shadow-md"
	>
		<div class="flex gap-4">
			<div class="w-full">
				<div>
					<label for={'name'} class="text-lg font-thin">{$t('admin.session.name')}</label>
					<input
						required
						name={'name'}
						placeholder="Votre nouvelle session"
						class="w-full p-4 border-b placeholder:font-thin placeholder:italic focus:border-white"
					/>
				</div>
			</div>
			<div>
				<label for="image">{$t('admin.session.image')}</label>
				<input
					type="file"
					name="image"
					accept="image/*"
					class="p-4 border-b appearance-none focus-within:bg-transparent"
				/>
			</div>
		</div>
		<div class="flex flex-col gap-4 p-4">
			<label for="scenarioId">{$t('admin.session.selectScenario')}</label>
			<select
				name="scenarioId"
				class="p-4 border-b appearance-none focus-within:bg-transparent text-gray-500"
				required
			>
				<option disabled>{$t('admin.session.chooseScenario')}</option>
				{#each data.scenarios as scenario}
					<option value={scenario.id}>{scenario.title}</option>
				{/each}
			</select>
		</div>
		<button
			type="submit"
			disabled={!validForm}
			class="self-center px-4 py-2 text-lg text-black transition-all ease-linear bg-white rounded disabled:cursor-not-allowed disabled:opacity-50"
		>
			{$t('admin.session.createTheSession')}
		</button>
	</form>

	{#if form?.success}
		<a
			class="self-center px-4 py-2 mt-4 text-lg font-light text-white border rounded"
			href="/sessions/{form?.session.slug}"
		>
			{$t('admin.session.goto')}</a
		>
	{:else if form?.error}
		<p class="p-4 text-red-500">{form.error}</p>
	{/if}
</div>
