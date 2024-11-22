<script lang="ts">
	import { enhance } from '$app/forms';
	import toast from 'svelte-french-toast';
	import { t } from 'svelte-i18n';
	import nProgress from 'nprogress';

	import { availableLocales } from '$lib/i18n';

	import type { ActionData } from './$types';
	import type { z } from 'zod';
	import { fullScenarioSchema } from '$lib/zschemas/scenario.schema';
	import { Pane } from 'svelte-tweakpane-ui';

	interface Props {
		form: ActionData;
	}
	let { form }: Props = $props();

	const formData: z.infer<typeof fullScenarioSchema> = $state({
		title: '',
		prologue: '',
		lang: 'fr',
		sides: [
			{
				title: ''
			}
		],
		firstNode: {
			title: '',
			text: '',
			author: ''
		},
		events: [
			{
				title: '',
				text: '',
				author: ''
			}
		],
		ends: [
			{
				title: '',
				text: ''
			}
		]
	});

	const issues = $derived.by(() => {
		try {
			fullScenarioSchema.parse(formData);
			return [];
		} catch (e) {
			const err = e as z.ZodError;
			return err.issues;
		}
	});

	$effect(() => {
		if (form?.error) {
			toast.error(form.error, { duration: 5000, position: 'bottom-center' });
		} else if (form?.success) {
			toast.success($t('scenario.success'), { duration: 3000, position: 'bottom-center' });
		}
	});
</script>

<div class="flex flex-col items-center text-white">
	<h1 class="p-4 text-3xl font-bold">{$t('scenario.newScenario')}</h1>
	<form
		method="POST"
		use:enhance={({ cancel }) => {
			nProgress.start();
			// try {
			// 	fullScenarioSchema.parse(formData);
			// } catch (error) {
			// 	nProgress.done();
			// 	cancel();
			// 	const err = error as z.ZodError;
			// 	const { message, path } = err.issues[0];
			// 	toast.error(path + ': ' + message, { duration: 5000, position: 'bottom-center' });
			// 	return;
			// }
			return async ({ update }) => {
				await update();
				nProgress.done();
			};
		}}
		action="?/createScenario"
		class="flex flex-col w-full gap-4 p-4 items-center text-white text-center border-t md:w-4/6"
	>
		<!-- Title and prologue -->
		<div class=" flex flex-col w-full gap-2">
			<label class="standardLabel">
				<input
					class="appearance-none rounded w-full h-full p-4"
					type="text"
					bind:value={formData.title}
					placeholder="Titre du scénario"
					name="title"
				/>
			</label>
			<label class="standardLabel">
				<textarea
					class="appearance-none block rounded w-full h-full p-4"
					placeholder="Prologue"
					bind:value={formData.prologue}
					name="prologue"
				></textarea>
			</label>
		</div>
		<!-- Lang -->
		<div class=" flex gap-2 justify-center w-full">
			{#each availableLocales as lang (lang)}
				<label
					class="standardLabel cursor-pointer h-full flex items-center justify-center {lang === formData.lang
						? ' ring-white ring-1 ring-inset'
						: 'text-white'}"
				>
					<input
						class=" appearance-none"
						type="radio"
						name="lang"
						bind:group={formData.lang}
						value={lang}
						checked={lang === formData.lang}
					/>
					<div>
						{lang}
					</div>
				</label>
			{/each}
		</div>
		<!-- First node -->
		<div class="flex flex-col gap-4 items-center w-full">
			<label class="standardLabel">
				<input
					class="rounded w-full h-full p-2"
					type="text"
					bind:value={formData.firstNode.title}
					placeholder={$t('scenario.firstNodeTitle')}
					name="firstNodeTitle"
				/>
			</label>
			<label class="standardLabel">
				<textarea
					class=" rounded block w-full h-full p-2"
					placeholder={$t('scenario.firstNodeText')}
					bind:value={formData.firstNode.text}
					name="firstNodeText"
				></textarea>
			</label>
			<label class="standardLabel">
				<input
					type="text"
					class=" rounded w-full h-full p-2"
					bind:value={formData.firstNode.author}
					placeholder={$t('scenario.firstNodeAuthor')}
					name="firstNodeAuthor"
				/>
			</label>
		</div>
		<!-- Sides -->
		<div class="standardLabel flex flex-col items-center gap-4 justify-center">
			<div class=" flex flex-wrap gap-4 justify-center items-center">
				{#each formData.sides as side, i (side)}
					<div class=" flex-col gap-2 flex">
						<h2 class="text-2xl font-bold">{$t('scenario.side')} {i + 1}</h2>
						<div class="flex gap-2 items-center">
							<label class="standardLabel">
								<input
									class=" w-full h-full p-2 rounded"
									type="text"
									bind:value={side.title}
									placeholder="Titre du côté"
									name="side"
								/>
							</label>
							<button
								class="rounded-md border px-4 py-2 {formData.sides.length <= 1
									? 'cursor-not-allowed text-gray-500 border-gray-500'
									: 'bg-black text-gray-50  '}"
								type="button"
								onclick={() => {
									formData.sides = formData.sides.filter((_, index) => index !== i);
								}}
								disabled={formData.sides.length <= 1}
							>
								{$t('scenario.delete')}
							</button>
						</div>
					</div>
				{/each}
			</div>
			<button
				class="rounded text-black px-4 w-60 py-2 font-bold bg-white"
				type="button"
				onclick={() => {
					formData.sides = [...formData.sides, { title: '' }];
				}}
			>
				{$t('scenario.add')}
			</button>
		</div>
		<!-- Events -->
		<div class="standardLabel flex flex-col items-center gap-4 p-4 justify-center">
			<div class=" flex flex-wrap gap-4 justify-center items-center">
				{#each formData.events as event, i (event)}
					<div class="flex flex-col justify-center items-center p-2 border-gray-800 border-l rounded-md">
						<div class="flex items-center justify-center flex-col gap-2">
							<h2 class="p-4 text-2xl font-bold">{$t('scenario.event')} {i + 1}</h2>
							<label class="standardLabel">
								<input
									class=" w-full h-full p-2 rounded"
									type="text"
									bind:value={event.title}
									placeholder="Titre de l'événement"
									name="eventTitle"
								/>
							</label>
							<label class="standardLabel">
								<textarea
									class=" appearance-none block w-full h-full p-2 rounded"
									bind:value={event.text}
									placeholder="Texte de l'événement"
									name="eventText"
								></textarea>
							</label>
							<label class="standardLabel">
								<input
									class=" w-full h-full p-2 rounded"
									type="text"
									bind:value={event.author}
									placeholder="Auteur de l'événement"
									name="eventAuthor"
								/>
							</label>
						</div>
						<button
							class="rounded-md border px-4 py-2 h-fit {formData.events.length <= 1
								? 'cursor-not-allowed text-gray-500 border-gray-500'
								: 'bg-black text-gray-50  '}"
							type="button"
							onclick={() => {
								formData.events = formData.events.filter((_, index) => index !== i);
							}}
							disabled={formData.events.length <= 1}
						>
							{$t('scenario.delete')}
						</button>
					</div>
				{/each}
			</div>
			<button
				class="rounded text-black px-4 w-60 py-2 font-bold bg-white"
				type="button"
				onclick={() => {
					formData.events = [...formData.events, { title: '', text: '', author: '' }];
				}}
			>
				{$t('scenario.add')}
			</button>
		</div>
		<div class="standardLabel flex flex-col items-center gap-4 justify-center">
			<div class="flex flex-wrap gap-4 justify-center items-center">
				{#each formData.ends as end, i (end)}
					<div class="flex flex-col items-center p-2 border-gray-800 border-l rounded-md">
						<h2 class="p-4 text-2xl font-bold">{$t('scenario.end')} {i + 1}</h2>
						<label class="standardLabel">
							<input
								class="w-full h-full p-2 rounded"
								type="text"
								bind:value={end.title}
								placeholder="Titre de la fin"
								name="endTitle"
							/>
						</label>
						<label class="standardLabel">
							<textarea
								class="appearance-none block w-full h-full p-2 rounded"
								bind:value={end.text}
								placeholder="Texte de la fin"
								name="endText"
							></textarea>
						</label>
						<button
							class="rounded-md border px-4 py-2 {formData.ends.length <= 1
								? 'cursor-not-allowed text-gray-500 border-gray-500'
								: 'bg-black text-gray-50'}"
							type="button"
							onclick={() => {
								formData.ends = formData.ends.filter((_, index) => index !== i);
							}}
							disabled={formData.ends.length <= 1}
						>
							{$t('scenario.delete')}
						</button>
					</div>
				{/each}
			</div>
			<button
				class="rounded text-black px-4 w-60 py-2 font-bold bg-white"
				type="button"
				onclick={() => {
					formData.ends = [...formData.ends, { title: '', text: '' }];
				}}
			>
				{$t('scenario.add')}
			</button>
		</div>
		<button
			class="rounded-md border px-4 py-2 h-fit disabled:cursor-not-allowed disabled:text-gray-500 disabled:border-gray-500 bg-black text-gray-50"
			type="submit"
			disabled={Boolean(issues.length)}
		>
			{$t('scenario.createYourScenario')}
		</button>
		{#if issues.length > 0}
			<div class=" bg-black p-4 grid grid-cols-2 grid-flow-row w-full gap-2 justify-center items-center">
				{#each issues as issue (issue)}
					<div class="bg-red-500 grow p-2 rounded-md flex flex-col items-center gap-2">
						<div>{issue.path.map((p) => $t('scenario.' + String(p))).join('.')}</div>
						<div>{$t(issue.message)}</div>
					</div>
				{/each}
			</div>
		{/if}
	</form>
</div>

<style lang="postcss">
	.standardLabel {
		@apply bg-black/90 shadow-lg backdrop-contrast-50 w-full rounded-md appearance-none p-4;
	}
</style>
