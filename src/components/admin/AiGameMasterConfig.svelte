<script lang="ts">
	import toast from 'svelte-french-toast';
	import { t } from 'svelte-i18n';
	import { Loader } from 'lucide-svelte';
	import type { AIConfig, AICapability, MistralAnalysisResponse } from '$types/ai';

	interface Props {
		aiConfig: AIConfig;
		sides: { title: string }[];
		ends: { title: string }[];
		lang: string;
	}

	let { aiConfig, sides, ends, lang }: Props = $props();

	let mistralLoading = $state(false);
	let mistralResult: MistralAnalysisResponse | null = $state(null);

	const showCensor = $derived(aiConfig.capabilities.includes('canCensor'));
	const showTrigger = $derived(aiConfig.capabilities.includes('canTriggerNodes'));
	const showEnd = $derived(aiConfig.capabilities.includes('canEndSession'));

	const capabilityList = $derived([
		{ id: 'canCensor', label: $t('ia.canCensor'), desc: $t('ia.canCensorDesc') },
		{ id: 'canTriggerNodes', label: $t('ia.canTriggerNodes'), desc: $t('ia.canTriggerNodesDesc') },
		{ id: 'canEndSession', label: $t('ia.canEndSession'), desc: $t('ia.canEndSessionDesc') }
	]);

	function toggleCapability(cap: AICapability) {
		if (aiConfig.capabilities.includes(cap)) {
			aiConfig.capabilities = aiConfig.capabilities.filter((c) => c !== cap);
		} else {
			aiConfig.capabilities = [...aiConfig.capabilities, cap];
		}
	}

	async function analyzeVision() {
		if (!aiConfig.vision || aiConfig.vision.trim().length < 10) return;
		mistralLoading = true;
		mistralResult = null;
		try {
			const res = await fetch('/api/ai/analyzeVision', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ vision: aiConfig.vision, lang })
			});
			if (!res.ok) {
				toast.error($t('ia.analysisError'), { position: 'bottom-center' });
				return;
			}
			const data: MistralAnalysisResponse = await res.json();
			mistralResult = data;
			aiConfig.capabilities = data.capabilities;
		} catch {
			toast.error($t('ia.analysisError'), { position: 'bottom-center' });
		} finally {
			mistralLoading = false;
		}
	}

	function addBannedWord() {
		aiConfig.script.bannedWords = [...(aiConfig.script.bannedWords ?? []), ''];
	}
	function removeBannedWord(i: number) {
		aiConfig.script.bannedWords = (aiConfig.script.bannedWords ?? []).filter((_, idx) => idx !== i);
	}

	function addTriggerRule() {
		aiConfig.script.triggerRules = [
			...(aiConfig.script.triggerRules ?? []),
			{ condition: '', node: { title: '', text: '', author: '', side: sides[0]?.title ?? '' }, requiresFired: [] }
		];
	}

	function toggleRequiresFired(ruleIndex: number, depIndex: number) {
		const rules = aiConfig.script.triggerRules ?? [];
		const rule = rules[ruleIndex];
		if (!rule) return;
		const deps = rule.requiresFired ?? [];
		if (deps.includes(depIndex)) {
			rule.requiresFired = deps.filter((d) => d !== depIndex);
		} else {
			rule.requiresFired = [...deps, depIndex];
		}
		aiConfig.script.triggerRules = [...rules];
	}
	function removeTriggerRule(i: number) {
		aiConfig.script.triggerRules = (aiConfig.script.triggerRules ?? []).filter(
			(_, idx) => idx !== i
		);
	}


</script>

<div class="flex flex-col gap-6 w-full">
	<!-- Vision -->
	<div class="flex flex-col gap-2">
		<label class="standardLabel flex flex-col gap-2">
			<span class="text-sm text-gray-300">{$t('ia.vision')} *</span>
			<span class="text-xs text-gray-400">{$t('ia.visionDesc')}</span>
			<textarea
				class="appearance-none block rounded w-full h-full p-2 bg-black/0 min-h-24"
				placeholder={$t('ia.visionPlaceholder')}
				bind:value={aiConfig.vision}
			></textarea>
		</label>
		<button
			class="rounded border px-4 py-2 text-sm flex items-center justify-center gap-2 disabled:cursor-not-allowed disabled:text-gray-500 disabled:border-gray-500 bg-black text-gray-50"
			type="button"
			disabled={mistralLoading || !aiConfig.vision || aiConfig.vision.trim().length < 10}
			onclick={analyzeVision}
		>
			{#if mistralLoading}
				<Loader class="w-4 h-4 animate-spin" />
				{$t('ia.analyzing')}
			{:else}
				{$t('ia.analyzeWithMistral')}
			{/if}
		</button>
		{#if mistralResult}
			<div class="standardLabel flex flex-col gap-2 text-sm text-left">
				<p class="text-gray-200">{mistralResult.explanation}</p>
				{#if !mistralResult.fullySupported}
					<p class="text-yellow-400">{$t('ia.notFullySupported')}</p>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Capabilities -->
	<div class="flex flex-col gap-3">
		<h4 class="text-lg font-semibold">{$t('ia.capabilities')}</h4>
		{#each capabilityList as { id, label, desc } (id)}
			<label class="standardLabel flex items-start gap-3 cursor-pointer">
				<input
					type="checkbox"
					class="rounded mt-1 shrink-0"
					checked={aiConfig.capabilities.includes(id as AICapability)}
					onchange={() => toggleCapability(id as AICapability)}
				/>
				<div class="flex flex-col text-left">
					<span>{label}</span>
					<span class="text-xs text-gray-400 mt-0.5">{desc}</span>
				</div>
			</label>
		{/each}
	</div>

	<!-- Banned words (canCensor) -->
	{#if showCensor}
		<div class="flex flex-col gap-3">
			<h4 class="text-lg font-semibold">{$t('ia.bannedWords')}</h4>
			<span class="text-xs text-gray-400">{$t('ia.bannedWordsDesc')}</span>
			<div class="flex flex-wrap gap-2">
				{#each aiConfig.script.bannedWords ?? [] as _, i (i)}
					<div class="flex gap-2 items-center">
						<label class="standardLabel w-auto">
							<input
								class="rounded p-2 bg-black/0 w-32"
								type="text"
								bind:value={aiConfig.script.bannedWords![i]}
								placeholder={$t('ia.bannedWords')}
							/>
						</label>
						<button
							class="rounded-md border px-3 py-2 text-sm bg-black text-gray-50"
							type="button"
							onclick={() => removeBannedWord(i)}
						>
							{$t('misc.delete')}
						</button>
					</div>
				{/each}
			</div>
			<button
				class="rounded text-black px-4 w-40 py-2 font-bold bg-white text-sm"
				type="button"
				onclick={addBannedWord}
			>
				{$t('misc.add')}
			</button>
		</div>
	{/if}

	<!-- Trigger rules (canTriggerNodes) -->
	{#if showTrigger}
		<div class="flex flex-col gap-3">
			<h4 class="text-lg font-semibold">{$t('ia.triggerRules')}</h4>
			<span class="text-xs text-gray-400">{$t('ia.triggerRulesDesc')}</span>
			{#each aiConfig.script.triggerRules ?? [] as rule, i (i)}
				<div class="standardLabel flex flex-col gap-3">
					<div class="flex justify-between items-center">
						<span class="font-semibold">{$t('ia.triggerRules')} {i + 1}</span>
						<button
							class="rounded-md border px-3 py-1 text-sm bg-black text-gray-50"
							type="button"
							onclick={() => removeTriggerRule(i)}
						>
							{$t('misc.delete')}
						</button>
					</div>
					<label class="standardLabel flex flex-col gap-1">
						<span class="text-xs text-gray-400">{$t('ia.triggerCondition')}</span>
						<span class="text-xs text-gray-500">{$t('ia.triggerConditionDesc')}</span>
						<textarea
							class="appearance-none block rounded w-full p-2 bg-black/0 min-h-16"
							placeholder={$t('ia.triggerCondition')}
							bind:value={rule.condition}
						></textarea>
					</label>
					{#if i > 0 && (aiConfig.script.triggerRules ?? []).length > 1}
						<div class="standardLabel flex flex-col gap-1">
							<span class="text-xs text-gray-400">{$t('ia.requiresFired')}</span>
							<span class="text-xs text-gray-500">{$t('ia.requiresFiredDesc')}</span>
							<div class="flex flex-wrap gap-2 mt-1">
								{#each (aiConfig.script.triggerRules ?? []).slice(0, i) as dep, di (di)}
									<label class="flex items-center gap-1.5 cursor-pointer text-sm">
										<input
											type="checkbox"
											class="rounded"
											checked={(rule.requiresFired ?? []).includes(di)}
											onchange={() => toggleRequiresFired(i, di)}
										/>
										<span class="text-gray-300">
											{$t('ia.triggerRules')} {di + 1}{dep.node.title ? ` — ${dep.node.title}` : ''}
										</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}
					<span class="text-xs text-gray-500 mt-1">{$t('ia.triggerNodeDesc')}</span>
					<label class="standardLabel flex flex-col gap-1">
						<span class="text-xs text-gray-400">{$t('scenario.title')}</span>
						<input
							class="rounded w-full p-2 bg-black/0"
							type="text"
							placeholder={$t('scenario.title')}
							bind:value={rule.node.title}
						/>
					</label>
					<label class="standardLabel flex flex-col gap-1">
						<span class="text-xs text-gray-400">{$t('scenario.text')}</span>
						<textarea
							class="appearance-none block rounded w-full p-2 bg-black/0 min-h-16"
							placeholder={$t('scenario.text')}
							bind:value={rule.node.text}
						></textarea>
					</label>
					<label class="standardLabel flex flex-col gap-1">
						<span class="text-xs text-gray-400">{$t('scenario.author')}</span>
						<input
							class="rounded w-full p-2 bg-black/0"
							type="text"
							placeholder={$t('scenario.author')}
							bind:value={rule.node.author}
						/>
					</label>
					<label class="standardLabel flex flex-col gap-1">
						<span class="text-xs text-gray-400">{$t('side.side')}</span>
						<span class="text-xs text-gray-500">{$t('ia.triggerSideDesc')}</span>
						<select class="rounded w-full p-2 bg-black/0" bind:value={rule.node.side}>
							{#each sides as side, si (si)}
								<option value={side.title}>{side.title || 'Side'}</option>
							{/each}
						</select>
					</label>
				</div>
			{/each}
			<button
				class="rounded text-black px-4 w-40 py-2 font-bold bg-white text-sm"
				type="button"
				onclick={addTriggerRule}
			>
				{$t('misc.add')}
			</button>
		</div>
	{/if}

	<!-- End condition (canEndSession) -->
	{#if showEnd}
		<div class="flex flex-col gap-3">
			<h4 class="text-lg font-semibold">{$t('ia.endCondition')}</h4>
			<span class="text-xs text-gray-400">{$t('ia.endConditionDesc')}</span>
			<div class="standardLabel flex flex-col gap-3">
				<label class="standardLabel flex flex-col gap-1">
					<span class="text-xs text-gray-400">{$t('ia.endCondition')}</span>
					<span class="text-xs text-gray-500">{$t('ia.endConditionFieldDesc')}</span>
					<textarea
						class="appearance-none block rounded w-full p-2 bg-black/0 min-h-16"
						placeholder={$t('ia.endCondition')}
						bind:value={aiConfig.script.endCondition!.condition}
					></textarea>
				</label>
				<label class="standardLabel flex flex-col gap-1">
					<span class="text-xs text-gray-400">{$t('scenario.end.end')}</span>
					<span class="text-xs text-gray-500">{$t('ia.endTitleDesc')}</span>
					<select
						class="rounded w-full p-2 bg-black/0"
						bind:value={aiConfig.script.endCondition!.endTitle}
					>
						{#each ends as end, ei (ei)}
							<option value={end.title}>{end.title || 'End'}</option>
						{/each}
					</select>
				</label>
			</div>
		</div>
	{/if}

</div>

<style lang="postcss">
	@reference "../../app.css";
	.standardLabel {
		@apply bg-gray-950/50 border border-gray-200/20 shadow-lg backdrop-blur-[2px] w-full rounded-md appearance-none p-4;
	}
</style>
