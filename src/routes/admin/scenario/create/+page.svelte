<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { enhance } from '$app/forms';
	import toast from 'svelte-french-toast';
	import { t } from 'svelte-i18n';
	import nProgress from 'nprogress';
	import { availableLocales } from '$lib/i18n';
	import { fullScenarioSchema, sideSchema } from '$lib/zschemas/scenario.schema';
	import { Sparkles, TriangleAlert } from 'lucide-svelte';
	import type { z } from 'zod';
	import type { ActionData } from './$types';
	import type { PreviewNode, Side } from '$types/pocketBase/TableTypes';
	import { PreviewGraph } from '$stores/graph/Classes/PreviewGraph.svelte';

	interface Props {
		form: ActionData;
	}
	let { form }: Props = $props();

	let svg: SVGElement | null = $state.raw(null);
	let graph: PreviewGraph | null = $state.raw(null);
	let preview = $state(true);

	const formData: z.input<typeof fullScenarioSchema> = $state({
		title: '',
		prologue: '',
		lang: 'fr',
		firstNode: {
			title: '',
			text: '',
			author: ''
		},
		ai: false,
		sides: [
			{
				title: ''
			},
			{
				title: ''
			}
		],
		events: [
			{
				title: '',
				text: '',
				author: ''
			}
		],
		triggers: [
			{
				title: '',
				text: '',
				author: '',
				triggerExpressions: '',
				conditions: ''
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
			toast.success($t('misc.success'), { duration: 3000, position: 'bottom-center' });
		}
		if (formData.ai) {
        	formData.events = [];
		} else {
			formData.triggers = [];
		}
	});

	function generateNodes() {
		if (!graph || !formData) return;
		untrack(() => {
			graph?.clearNodes();
			const startNode = {
				id: 'startNodeId',
				type: 'startNode',
				title: formData.firstNode.title,
				text: formData.firstNode.text,
				parent: 'null',
				side: 'start',
				sideNumber: 0
			} as PreviewNode;
			graph?.addNode(startNode);
			formData.sides.forEach((side, i) => {
				if (!side.title) return;
				const node = {
					id: `side-${i}`,
					type: 'contribution',
					title: side.title,
					text: 'Message de test',
					parent: 'startNodeId',
					side: side.title,
					sideNumber: i
				} as PreviewNode;
				graph?.addNode(node);
			});
			formData.events?.forEach((event, i) => {
				if (!event.title) return;
				const node = {
					id: `event-${i}`,
					type: 'event',
					title: event.title,
					text: 'Message de test',
					parent: 'startNodeId',
					side: 'event',
					sideNumber: i
				} as PreviewNode;
				graph?.addNode(node);
			});
		});
	}

	onMount(() => {
		const data = localStorage.getItem('scenario');
		if (data) {
			const parsed = JSON.parse(data);
			formData.title = parsed.title;
			formData.prologue = parsed.prologue;
			formData.lang = parsed.lang;
			formData.firstNode = parsed.firstNode;
			formData.ai = parsed.ai;
			formData.sides = parsed.sides;
			formData.events = parsed.events;
			formData.triggers = parsed.triggers;
			formData.ends = parsed.ends;
			if (preview) {
				generateNodes();
			} else {
				graph?.clearNodes();
			}
		}
		$effect(() => {
			localStorage.setItem('scenario', JSON.stringify(formData));
			if (preview) {
				generateNodes();
			} else {
				graph?.clearNodes();
			}
		});
		if (!svg) return;
		graph = new PreviewGraph(svg, [], [], {
			width: 500,
			height: 500
		});
	});
</script>

<div class="flex flex-col items-center text-white pb-5">
	<h1 class="p-4 text-3xl font-bold">{$t('admin.scenario.newScenario')}</h1>
	<form
		method="POST"
		use:enhance={({ cancel }) => {
			nProgress.start();
			return async ({ update }) => {
				await update();
				nProgress.done();
			};
		}}
		action="?/createScenario"
		class="flex flex-col w-full gap-4 p-4 items-center text-white text-center border-t md:w-4/6"
	>
		<!-- Title and prologue -->
		<h3 class=" text-white text-3xl text-center w-full mt-5">
			{$t('admin.scenario.informations')}
		</h3>
		<div class=" flex flex-col w-full gap-2">
			<label class="standardLabel">
				<input
					class="appearance-none rounded w-full h-full p-4 bg-black/0"
					type="text"
					bind:value={formData.title}
					placeholder={$t('scenario.title')}
					name="title"
				/>
			</label>
			<label class="standardLabel">
				<textarea
					class="appearance-none block rounded w-full h-full p-4 bg-black/0"
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

		<!-- AI -->
		<h3 class=" text-white text-3xl text-center w-full mt-5">
			{$t('ia.ia')}
		</h3>
		<div class="flex">
			<label class="standardLabel flex gap-4">
				{$t('admin.scenario.useAi')}
				<input
					class="rounded p-2"
					type="checkbox"
					value={formData.ai}
					bind:checked={formData.ai}
					name="useAi"
				/>
			</label>
		</div>

		<!-- First node -->
		<h3 class=" text-white text-3xl text-center w-full mt-5">
			{$t('scenario.firstNode.firstNode')}
		</h3>
		<div class="flex flex-col gap-4 items-center w-full">
			<label class="standardLabel">
				<input
					class="rounded w-full h-full p-2 bg-black/0"
					type="text"
					bind:value={formData.firstNode.title}
					placeholder={$t('scenario.firstNode.firstNodeTitle')}
					name="firstNodeTitle"
				/>
			</label>
			<label class="standardLabel">
				<textarea
					class="rounded block w-full h-full p-2 bg-black/0"
					placeholder={$t('scenario.firstNode.firstNodeText')}
					bind:value={formData.firstNode.text}
					name="firstNodeText"
				></textarea>
			</label>
			<label class="standardLabel">
				<input
					type="text"
					class="rounded w-full h-full p-2 bg-black/0"
					bind:value={formData.firstNode.author}
					placeholder={$t('scenario.firstNode.firstNodeAuthor')}
					name="firstNodeAuthor"
				/>
			</label>
		</div>

		<!-- Sides -->
		<h3 class=" text-white text-3xl text-center w-full mt-5">
			{$t('side.sides')}
		</h3>
		<div class="standardLabel flex flex-col items-center gap-4 justify-center">
			<div class=" flex flex-wrap gap-4 justify-center items-center">
				{#each formData.sides as side, i (side)}
					<div class=" flex-col gap-2 flex">
						<h2 class="text-2xl font-bold">{$t('side.side')} {i + 1}</h2>
						<div class="flex gap-2 items-center">
							<label class="standardLabel">
								<input
									class="w-full h-full p-2 rounded bg-black/0"
									type="text"
									bind:value={side.title}
									placeholder={$t('side.title')}
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
								{$t('misc.delete')}
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
				{$t('misc.add')}
			</button>
		</div>

		{#if !formData.ai}
			<!-- Events -->
			<h3 class=" text-white text-3xl text-center w-full mt-5">
				{$t('scenario.event.events')}
			</h3>
			<div class="w-full standardLabel flex flex-col items-center gap-4 p-4 justify-center">
				<div class="flex flex-wrap gap-4 justify-center items-center">
					{#each formData.events ?? [] as event, i (event)}
						<div class="flex flex-col justify-center items-center p-2 border-gray-800 border-l rounded-md">
							<div class="flex items-center justify-center flex-col gap-2">
								<h2 class="p-4 text-2xl font-bold">{$t('scenario.event.event')} {i + 1}</h2>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={event.title}
										placeholder={$t('scenario.event.title')}
										name="eventTitle"
									/>
								</label>
								<label class="standardLabel">
									<textarea
										class="appearance-none block w-full h-full p-2 rounded bg-black/0"
										bind:value={event.text}
										placeholder={$t('scenario.event.text')}
										name="eventText"
									></textarea>
								</label>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={event.author}
										placeholder={$t('scenario.event.author')}
										name="eventAuthor"
									/>
								</label>
							</div>
							<button
								class="rounded-md border mt-2 px-4 py-2 h-fit {formData.events?.length ?? 0 <= 1
									? 'cursor-not-allowed text-gray-500 border-gray-500'
									: 'bg-black text-gray-50  '}"
								type="button"
								onclick={() => {
									formData.events = formData.events?.filter((_, index) => index !== i);
								}}
								disabled={(formData.events?.length ?? 0) <= 1}
							>
								{$t('misc.delete')}
							</button>
						</div>
					{/each}
				</div>
				<button
					class="rounded text-black mt-2 mb-1 px-4 w-60 py-2 font-bold bg-white"
					type="button"
					onclick={() => {
						formData.events = [...(formData.events ?? []), { title: '', text: '', author: '' }];
					}}
				>
					{$t('misc.add')}
				</button>
			</div>
		{:else}
			<!-- Triggers -->
			<h3 class=" text-white text-3xl text-center w-full mt-5">
				{$t('Triggers pour l\'IA')}
			</h3>
			<p class="text-gray-300 text-sm mb-2 max-w-2xl text-center">
				Chaque noeud trigger doit contenir une ou plusieurs expressions déclencheuses (séparées par des virgules), des conditions éventuelles (séparées par des virgules) qui correspondent au numéro des triggers devant avoir été déclenchés avant pour que celui-ci puisse l'être aussi, et l'auteur du trigger. 
				Ces triggers serviront à détecter des situations ou mots-clés spécifiques dans le scénario.
			</p>
			<div class="w-full standardLabel flex flex-col items-center gap-4 p-4 justify-center">
				<div class="flex flex-wrap gap-4 justify-center items-center">
					{#each formData.triggers ?? [] as trigger, i (trigger)}
						<div class="flex flex-col justify-center items-center p-2 border-gray-800 border-l rounded-md">
							<div class="flex items-center justify-center flex-col gap-2">
								<h2 class="p-4 text-2xl font-bold">Trigger {i + 1}</h2>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={trigger.title}
										placeholder="Titre du noeud déclenché"
										name="triggerTitle"
									/>
								</label>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={trigger.text}
										placeholder="Texte du noeud délenché"
										name="triggerText"
									/>
								</label>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={trigger.triggerExpressions}
										placeholder="Triggers (séparés par ,)"
										name="triggerExpressions"
									/>
								</label>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={trigger.conditions}
										placeholder="Conditions (séparées par ,)"
										name="conditions"
									/>
								</label>
								<label class="standardLabel">
									<input
										class="w-full h-full p-2 rounded bg-black/0"
										type="text"
										bind:value={trigger.author}
										placeholder="Auteur"
										name="triggerAuthor"
									/>
								</label>
							</div>
							<button
								class="rounded-md border mt-2 px-4 py-2 h-fit {formData.triggers?.length ?? 0 <= 1
									? 'cursor-not-allowed text-gray-500 border-gray-500'
									: 'bg-black text-gray-50  '}"
								type="button"
								onclick={() => {
									formData.triggers = formData.triggers?.filter((_, index) => index !== i);
								}}
								disabled={(formData.triggers?.length ?? 0) <= 1}
							>
								{$t('misc.delete')}
							</button>
						</div>
					{/each}
				</div>
				<button
					class="rounded text-black mt-2 mb-1 px-4 w-60 py-2 font-bold bg-white"
					type="button"
					onclick={() => {
						formData.triggers = [...(formData.triggers ?? []), { title: '', text: '', author: '', triggerExpressions: '', conditions: '' }];
					}}
				>
					{$t('misc.add')}
				</button>
			</div>
		{/if}

		<!-- Ends -->
		<h3 class="text-white text-3xl text-center w-full mt-5">
			{$t('scenario.end.ends')}
		</h3>
		<div class="standardLabel flex flex-col items-center gap-4 justify-center">
			<div class="flex flex-wrap gap-4 justify-center items-center">
				{#each formData.ends as end, i (end)}
					<div class="flex flex-col items-center p-2 border-gray-800 border-l rounded-md">
						<h2 class="p-4 text-2xl font-bold">{$t('scenario.end.end')} {i + 1}</h2>
						<label class="standardLabel">
							<input
								class="w-full h-full p-2 rounded bg-black/0"
								type="text"
								bind:value={end.title}
								placeholder={$t('scenario.end.title')}
								name="endTitle"
							/>
						</label>
						<label class="standardLabel">
							<textarea
								class="appearance-none block w-full h-full p-2 rounded"
								bind:value={end.text}
								placeholder={$t('scenario.end.text')}
								name="endText"
							></textarea>
						</label>
						<button
							class="rounded-md border mt-2 px-4 py-2 {formData.ends.length <= 1
								? 'cursor-not-allowed text-gray-500 border-gray-500'
								: 'bg-black text-gray-50'}"
							type="button"
							onclick={() => {
								formData.ends = formData.ends.filter((_, index) => index !== i);
							}}
							disabled={formData.ends.length <= 1}
						>
							{$t('misc.delete')}
						</button>
					</div>
				{/each}
			</div>
			<button
				class="rounded text-black mt-2 mb-1 px-4 w-60 py-2 font-bold bg-white"
				type="button"
				onclick={() => {
					formData.ends = [...formData.ends, { title: '', text: '' }];
				}}
			>
				{$t('misc.add')}
			</button>
		</div>
		<button
			class="rounded-md border px-4 py-2 h-fit disabled:cursor-not-allowed disabled:text-gray-500 disabled:border-gray-500 bg-black text-gray-50"
			type="submit"
			disabled={Boolean(issues.length)}
		>
			{$t('admin.scenario.createYourScenario')}
		</button>

		<!-- Errors -->
		<div class="h-36 p-4 rounded-md overflow-auto">
			{#if issues.length > 0}
				<div class="bg-black flex flex-col items-center gap-4">
					<h3 class=" font-semibold text-xl flex items-center gap-2 k">
						<TriangleAlert class="w-8 h-8" />
						{$t('errors.scenario.notValid')}
						<TriangleAlert class="w-8 h-8" />
					</h3>
					<div class=" grid grid-cols-2 grid-flow-row w-full gap-4 justify-center items-center">
						{#each issues as issue (issue)}
							<div class="bg-red-500 grow p-2 rounded-md flex flex-col items-center gap-2">
								<div>{$t(issue.message)}</div>
							</div>
						{/each}
					</div>
				</div>
			{:else}
				<div class="bg-green-500 w-full p-4 rounded-md flex flex-col justify-center items-center mt-5">
					<h3 class=" font-semibold text-xl flex items-center gap-2">
						<Sparkles class="w-7 h-7" />
						<div>{$t('admin.scenario.scenarioIsValide')}</div>
						<Sparkles class="w-7 h-7" />
					</h3>
				</div>
			{/if}
		</div>
	</form>
	<!-- Session preview -->
	<h3 class=" text-white text-3xl mt-10 mb-4 text-center w-full">
		{$t('admin.session.preview')}
	</h3>
	<label class="rounded-md border px-4 py-2 bg-black text-gray-50">
		{$t('admin.session.preview')}
		<input type="checkbox" class="ml-1" bind:checked={preview} />
	</label>
	<div class=" text-gray-200 relative w-fit h-fit p-0 m-4">
		<svg
			bind:this={svg}
			width="500"
			height="500"
			class="relative bg-dotted-gray bg-dotted-40 bg-black border border-white/20 rounded-md"
		>
		</svg>
		<div class=" absolute top-2 left-2 border border-white/20 bg-black p-2 rounded-md">
			{$t('scenario.title')} :
			<span class=" text-white font-bold">
				{formData.title}
			</span>
		</div>
		<div class="absolute left-2 bottom-2 border border-white/20 bg-black p-2 rounded-md">
			{$t('admin.scenario.language')} :
			<span class=" text-white font-bold">
				{formData.lang?.toUpperCase()}
			</span>
		</div>
		<div class="absolute right-2 bottom-2 border border-white/20 bg-black p-2 rounded-md">
			{$t('ia.ia')} :
			<span class=" text-white font-semibold">
				{formData.ai ? $t('misc.yes') : $t('misc.no')}
			</span>
		</div>
	</div>
</div>

<style lang="postcss">
	.standardLabel {
		@apply bg-gray-950/50 border border-gray-200/20 shadow-lg backdrop-blur-[2px] w-full rounded-md appearance-none p-4;
	}
</style>
