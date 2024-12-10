<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';
	import { LoaderPinwheel } from 'lucide-svelte';
	import { pb } from '$lib/client/pocketbase';
	import toast from 'svelte-french-toast';
	import { initStores, mapNodeSides } from './utils';
	import { titleStore } from '$stores/titles/index.svelte';
	import { buildLinks } from '$lib/sessions';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';
	import { t } from 'svelte-i18n';
	import GraphUi from '$components/graph/GraphUI.svelte';
	import MainGraph from '$components/graph/MainGraph.svelte';
	import type { PageServerData } from './$types';
	import type { LayoutServerData } from '../../$types';
	import type { GraphNode, Side } from '$types/pocketBase/TableTypes';
	import graph1 from '$lib/assets/graphe1.png';
	import { linksStore, nodesStore } from '$stores/graph';
	import { SvelteURL } from 'svelte/reactivity';
	import { pseudoSchema } from '$lib/zschemas/pseudo.schema';

	interface Props {
		data: PageServerData & LayoutServerData;
	}
	let { data }: Props = $props();
	let { events = [], user = null, nodesPromise, ends = [], sides, iaConnected = false, scenario } = data;

	let sessionData = $state(data.sessionData);

	// Intro related
	let prologueSeen = $state(false);
	let userSideId: string | null = $state(null);
	let validSide = $state(false);
	let pseudo: string | null = $state(null);
	let validPseudo = $derived(pseudoSchema.safeParse(pseudo).success);
	let pseudoLocked = $state(false);

	// ? wierd hack to make the admin reactive on page reload
	let admin = $derived($page.data.isAdmin as boolean);
	let sessionTitle = $derived.by(() => {
		return (admin ? 'ADMIN - ' : '') + data.sessionData.name;
	});

	function manageQueryStrings() {
		// update query params with admin status
		const url = new URL(location.href);
		if (admin) {
			url.searchParams.set('admin', admin.toString());
		} else {
			url.searchParams.delete('admin');
		}
		replaceState(url.toString(), '');
	}

	async function init() {
		const nodes = mapNodeSides(await nodesPromise, sides);
		const links = buildLinks(nodes);
		initStores(nodes, links);
		manageQueryStrings();
		titleStore.setNavTitle(sessionTitle);

		if (scenario?.ai && iaConnected) {
			toast.success($t('ia.connected'), {
				position: 'top-left'
			});
		}
	}

	function filterNodeBySide() {
		// Hide events from other side if it's an AI scenario
		const filteredText = $t('inSession.eventHidden');
		const filteredEventNodes = $nodesStore.map((node) => {
			if (node.type === 'event' && node.side && node.side !== userSideId) {
				node.text = filteredText;
				node.title = filteredText;
				node.author = filteredText;
				node.type = 'hidden';
			}
			return node;
		});
		nodesStore.set(filteredEventNodes);
		linksStore.set(buildLinks(filteredEventNodes));
	}

	function handleSideSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (userSideId) {
			localStorage.setItem('side_' + sessionData.id, userSideId);
			validSide = true;
			toast.success($t('side.sideSaved'), {
				position: 'bottom-center'
			});
			filterNodeBySide();
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

	onMount(async () => {
		await init();
		prologueSeen = new URL(location.href).searchParams.get('prologueSeen') === 'true';
		userSideId = localStorage.getItem('side_' + sessionData.id);
		pseudo = localStorage.getItem('pseudo_' + sessionData.id);
		if (scenario?.ai && userSideId) {
			validSide = true;
			filterNodeBySide();
		}
		if (validPseudo) {
			pseudoLocked = true;
		}
	});
	onDestroy(() => {
		mainGraphStore.selectedNode = null;
	});
</script>

<svelte:head>
	<title>{sessionTitle}</title>
	<meta content={sessionData.expand?.scenario?.prologue} property="description" />
	<meta content={sessionData.image ? pb.files.getUrl(sessionData, sessionData.image) : graph1} property="og:image" />
	<meta content={sessionData.name} property="og:title" />
	<meta content={sessionData.expand?.scenario?.prologue} property="og:description" />
	<meta content="Babel Révolution" property="og:site_name" />
	<meta content={$page.url.href} property="og:url" />
</svelte:head>

{#await data.nodesPromise}
	<div class=" w-full h-screen flex justify-center items-center bg-black">
		<LoaderPinwheel color="white" class="w-20 z-50 opacity-100 h-20 loader animate-spin" />
	</div>
{:then}
	<div class="">
		{#if prologueSeen && (admin || (pseudoLocked && pseudo && userSideId))}
			<GraphUi bind:session={sessionData} {admin} {user} {events} {pseudo} {userSideId} {ends} {sides} />
			<MainGraph sessionId={sessionData.id} {sides} />
		{:else}
			<div
				class="fixed h-screen overflow-auto w-screen top-0 z-40 flex justify-center items-center bg-dotted-gray bg-dotted-40 bg-black"
			>
				<div
					class="flex items-center flex-col gap-8 w-5/6 lg:w-2/3 border-gray-100 backdrop-blur-[2px] border p-8 rounded-lg bg-gray-800/10"
				>
					<h1 class="text-2xl font-bold text-center p-0">{$t('scenario.prologue')}</h1>
					<p
						class="text-balance h-40 overflow-auto border border-gray-200/30 p-2 rounded leading-7 text-gray-300"
					>
						<!-- TODO: use rich text editor -->
						{@html scenario?.prologue}
					</p>
					<div
						class="flex items-center gap-8 flex-col relative rounded {admin
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
						{#if scenario?.ai}
							<form
								onsubmit={handleSideSubmit}
								class:opacity-10={admin}
								class="flex flex-col gap-4 items-center"
							>
								<select class="p-4 border border-gray-100 rounded w-full" bind:value={userSideId}>
									<option disabled value={null} selected>{$t('side.chooseSide')}</option>
									{#each sides as side}
										<option
											disabled={validSide && !!userSideId && side.id !== userSideId}
											value={side.id}>{side.name}</option
										>
									{/each}
								</select>
								<button
									disabled={validSide}
									type="submit"
									class="font-bold border hover:bg-black disabled:opacity-50 border-gray-200 py-2 px-4 rounded"
								>
									{validSide ? $t('side.sideChosen') : $t('side.choose')}
								</button>
							</form>
						{/if}
						<form class:opacity-10={admin} class="flex flex-col gap-2" onsubmit={handlePseudoSubmit}>
							<input
								disabled={pseudoLocked}
								type="text"
								class="p-4 border border-gray-100 rounded w-fit disabled:opacity-50"
								placeholder={$t('user.pseudo')}
								bind:value={pseudo}
							/>
							<button
								disabled={pseudoLocked || !validPseudo}
								type="submit"
								class="font-bold border hover:bg-black disabled:opacity-50 border-gray-200 py-2 px-4 rounded"
							>
								{pseudoLocked ? $t('user.pseudoLocked') : $t('misc.submit')}
							</button>
							{#if pseudoLocked}
								<div class=" flex gap-2">
									<div>{$t('user.yourPseudo')}</div>
									<div class=" text-white">
										{pseudo}
									</div>
								</div>
							{/if}
						</form>
					</div>
					<button
						type="button"
						disabled={scenario?.ai && !validSide}
						onclick={handlePrologueSeen}
						class="font-bold w-fit self-center border float-end border-gray-200 py-2 px-4 rounded disabled:opacity-50 hover:bg-black hover:border-white"
					>
						{$t('misc.start')}
					</button>
				</div>
			</div>
		{/if}
	</div>
{/await}
