<script lang="ts">
	import { SvelteURL } from 'svelte/reactivity';
	import { replaceState } from '$app/navigation';
	import { t } from 'svelte-i18n';
	import toast from 'svelte-french-toast';

	let {
		graph,
		validSide,
		sessionData,
		scenario,
		validPseudo,
		admin,
		sides,
		userSideId = $bindable(),
		sideLocked = $bindable(),
		pseudo = $bindable(),
		pseudoLocked = $bindable(),
		prologueSeen = $bindable()
	} = $props();

	function handleSideSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (validSide && userSideId) {
			localStorage.setItem('side_' + sessionData.id, userSideId);
			sideLocked = true;
			toast.success($t('side.sideSaved'), {
				position: 'bottom-center'
			});
			if (scenario?.ai) {
				graph.filterNodeBySide(userSideId);
			}
		}
	}

	function handlePrologueSeen() {
		const url = new SvelteURL(location.href);
		prologueSeen = true;
		if (prologueSeen) {
			url.searchParams.set('prologueSeen', 'true');
		} else {
			url.searchParams.delete('prologueSeen');
		}
		replaceState(url.toString(), '');
	}

	function handlePseudoSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (validPseudo && pseudo) {
			localStorage.setItem('pseudo_' + sessionData.id, pseudo);
			pseudoLocked = true;
		}
	}
</script>

<div
	class="fixed h-screen overflow-auto w-screen top-0 z-40 flex justify-center items-center bg-dotted-gray bg-dotted-40 bg-black"
>
	<div
		class="flex items-center flex-col gap-8 w-5/6 lg:w-2/3 border-gray-100 backdrop-blur-[2px] border p-8 rounded-lg bg-gray-800/10"
	>
		<h1 class="text-2xl font-bold text-center p-0">{$t('scenario.prologue')}</h1>
		<p class="text-balance h-40 overflow-auto border border-gray-200/30 p-2 rounded leading-7 text-gray-300">
			{@html scenario?.prologue}
		</p>
		{#if !sessionData.completed}
			<div
				class="flex items-center md:items-start w-full md:justify-around gap-8 flex-col md:flex-row relative rounded {admin
					? 'border border-gray-200 p-2'
					: ''}"
			>
				{#if admin}
					<div
						class="text-white h-full w-full flex items-center justify-center text-xl top-[50%] left-[50%] -translate-x-[50%] -translate-y-[50%] absolute opacity-100"
					>
						{$t('admin.youAreAdmin')}
					</div>
				{/if}
				<form onsubmit={handleSideSubmit} class:opacity-10={admin} class="flex flex-col gap-4 items-start">
					<select
						disabled={sideLocked}
						class="p-2 h-12 border border-gray-100 disabled:opacity-50 rounded w-full"
						bind:value={userSideId}
					>
						<option disabled value={null} selected>{$t('side.chooseSide')}</option>
						{#each sides as side}
							<option disabled={sideLocked} value={side.id} class="text-gray-500">{side.name}</option>
						{/each}
					</select>
					<button
						disabled={sideLocked}
						type="submit"
						class="font-bold border h-12 hover:bg-black disabled:opacity-50 border-gray-200 py-2 px-4 rounded {sideLocked
							? 'border-red-400 text-red-400'
							: ''}"
					>
						{sideLocked ? $t('side.sideChosen') : $t('side.choose')}
					</button>
				</form>
				<form class:opacity-10={admin} class="flex flex-col gap-4 items-start" onsubmit={handlePseudoSubmit}>
					<input
						disabled={pseudoLocked}
						type="text"
						class="p-4 border h-12 border-gray-100 text-gray-500 rounded w-fit disabled:opacity-50"
						placeholder={$t('user.pseudo')}
						bind:value={pseudo}
					/>
					<button
						disabled={pseudoLocked || !validPseudo}
						type="submit"
						class="font-bold border h-12 hover:bg-black w-full disabled:opacity-50 border-gray-200 py-2 px-4 rounded {pseudoLocked
							? 'border-red-400 text-red-400'
							: ''}"
					>
						{pseudoLocked ? $t('user.pseudoLocked') : $t('misc.submit')}
					</button>
					<!-- {#if pseudoLocked}
						<div class=" flex gap-2">
							<div>{$t('user.yourPseudo')}</div>
							<div class=" text-white">
								{pseudo}
							</div>
						</div>
					{/if} -->
				</form>
			</div>
		{/if}
		<button
			type="button"
			disabled={!sessionData.completed && (!admin && (!sideLocked || !pseudoLocked))}
			onclick={handlePrologueSeen}
			class="font-bold w-fit self-center border float-end border-gray-200 py-2 px-4 rounded disabled:opacity-50 hover:bg-black hover:border-white"
		>
			{$t('misc.start')}
		</button>
	</div>
</div>
