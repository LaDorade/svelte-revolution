<script lang="ts">
	import { t } from 'svelte-i18n';
	import toast from 'svelte-french-toast';
	import { getCurrentSessionCtx } from '$stores/session.svelte';
	import { pseudoSchema } from '$lib/zschemas/pseudo.schema';

	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import Button from '$components/Button.svelte';

	interface Props{
		graph: MainGraph | null;
	}

	let {
		graph,
	}: Props = $props();

	const currentSession = getCurrentSessionCtx();

	let userSideId: string | null = $state(currentSession.sessionProfile.choosedSideId ?? null);
	let pseudo: string | null = $state(currentSession.sessionProfile.pseudo ?? null);

	let sideValid = $derived.by(() => {
		if (currentSession.sessionProfile.choosedSideId) return true;

		if (!userSideId) return false;

		return currentSession.sides.some(side => side.id === userSideId);
	});
	let pseudoValid = $derived.by(() => {
		if (currentSession.sessionProfile.pseudo) return true;

		if (!pseudo) return false;

		const result = pseudoSchema.safeParse(pseudo);
		return result.success;
	});

	function handleSideSubmit(e: SubmitEvent) {
		e.preventDefault();
		console.log(sideValid);
		
		if (sideValid && userSideId) {
			currentSession.setSide(userSideId);
			// When there AI, we filter the graph according to the chosen side
			if (currentSession.scenario.ai && currentSession.ai) {
				graph?.filterNodeBySide(userSideId);
			}
		} else {
			// TODO: translation
			toast.error($t('side.chooseSideError'), {
				position: 'top-left',
			});
		}
	}

	function handlePseudoSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (pseudoValid && pseudo) {
			currentSession.setPseudo(pseudo);
		} else {
			toast.error($t('user.invalidPseudo'), {
				position: 'top-left',
			});
		}
	}
</script>

<div
	class="fixed h-screen overflow-auto w-screen top-0 z-40 flex justify-center items-center bg-dotted-gray bg-dotted-40"
>
	<div
		class="flex items-center flex-col gap-8 w-5/6 lg:w-2/3 border-gray-100 backdrop-blur-[2px] border p-8 rounded-lg bg-gray-800/10"
	>
		<h1 class="text-2xl font-bold text-center p-0">{$t('scenario.prologue')}</h1>
		<p class="text-balance h-40 overflow-auto border border-gray-200/30 p-2 rounded leading-7 text-gray-300">
			<!-- eslint-disable-next-line svelte/no-at-html-tags-->
			{@html currentSession.scenario.prologue}
		</p>
		{#if !currentSession.session.completed}
			<div
				class="grid md:grid-cols-2 w-full md:justify-around gap-8 flex-col md:flex-row relative rounded
					{currentSession.admin.isAdmin ? 'border border-gray-200 p-2' : ''}"
			>
				{#if currentSession.admin.isAdmin}
					<div
						class="text-white h-full w-full flex items-center justify-center text-xl top-[50%] left-[50%] -translate-x-[50%] -translate-y-[50%] absolute opacity-100"
					>
						{$t('admin.youAreAdmin')}
					</div>
				{/if}
				<form onsubmit={handleSideSubmit} class:opacity-10={currentSession.admin.isAdmin} class="flex flex-col gap-4 items-start">
					<select
						class="p-2 h-12 border border-gray-100 disabled:opacity-50 rounded w-full"
						bind:value={userSideId}
						disabled={currentSession.userCanAccess}
					>
						<option value="" disabled selected class="text-gray-500">
							{$t('side.chooseSide')}
						</option>
						{#each currentSession.sides as side (side.id)}
							<option
								selected={currentSession.sessionProfile.choosedSideId === side.id} 
								value={side.id} 
								class="text-gray-500">
								{side.name}
							</option>
						{/each}
					</select>
					<Button
						type="submit"
						disabled={(
							currentSession.userCanAccess ||
							!currentSession.sessionProfile.choosedSideId && !sideValid
						)}
						class="w-full"
						variant="ghost"
					>
						{currentSession.sessionProfile.choosedSideId ? $t('side.sideChosen') : $t('side.choose')}
					</Button>
				</form>
				<form class:opacity-10={currentSession.admin.isAdmin} class="flex flex-col gap-4 items-start w-full" onsubmit={handlePseudoSubmit}>
					<input
						type="text"
						class="p-4 border h-12 border-gray-100 text-gray-500 rounded w-fit disabled:opacity-50 w-full"
						placeholder={$t('user.pseudo')}
						bind:value={pseudo}
						disabled={currentSession.userCanAccess}
					/>
					<Button
						type="submit"
						disabled={
							currentSession.userCanAccess ||
								(!currentSession.sessionProfile.pseudo && !pseudoValid)
						}
						class="w-full"
						variant="ghost"
					>
						{currentSession.sessionProfile.pseudo ? $t('user.pseudoChosen') : $t('misc.submit')}
					</Button>
				</form>
			</div>
		{/if}
		<Button
			variant="primary"
			type="button"
			disabled={!currentSession.session.completed && 
				(!currentSession.admin.isAdmin && 
					(!currentSession.sessionProfile.choosedSideId || !currentSession.sessionProfile.pseudo))}
			onclick={() => {
				currentSession.userWantAccess = true;
			}}
		>
			{$t('misc.start')}
		</Button>
	</div>
</div>
