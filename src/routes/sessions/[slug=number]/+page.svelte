<script lang="ts">
	import { onDestroy, onMount, untrack } from 'svelte';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';
	import { LoaderPinwheel } from 'lucide-svelte';
	import { pb } from '$lib/client/pocketbase';
	import toast from 'svelte-french-toast';
	import { initStores } from './utils';
	import { titleStore } from '$stores/titles/index.svelte';
	import { buildLinks } from '$lib/sessions';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';
	import { t } from 'svelte-i18n';
	import GraphUi from '$components/graph/GraphUI.svelte';
	import MainGraph from '$components/graph/MainGraph.svelte';
	import type { PageServerData } from './$types';
	import type { LayoutServerData } from '../../$types';
	import type { Side } from '$types/pocketBase/TableTypes';
	import graph1 from '$lib/assets/graphe1.png';
	import { linksStore, nodesStore } from '$stores/graph';
	import { SvelteURL } from 'svelte/reactivity';

	interface Props {
		data: PageServerData & LayoutServerData;
	}
	let { data }: Props = $props();
	let { events = [], user = null, nodesPromise, ends = [], sides, iaConnected = false, scenario } = data;

	let sessionData = $state(data.sessionData);

	// Intro related
	let prologueSeen = $state(false);
	let userSideId: string | null = $state(null);
	let lockedSide = $state(false);

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
		const nodes = (await nodesPromise).map((n) => {
			return {
				...n,
				sideNumber: sides.find((s: Side) => s.id === n.side)?.number ?? 0
			};
		});
		const links = buildLinks(nodes);
		initStores(nodes, links);
		manageQueryStrings();
		titleStore.setNavTitle(sessionTitle);

		if (iaConnected) {
			toast.success($t('ia.iaIsConnected'), {
				position: 'top-left'
			});
		}
	}

	function handleSideSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (userSideId) {
			localStorage.setItem('side_' + sessionData.id, userSideId);
			lockedSide = true;
			toast.success($t('prologue.sideSaved'), {
				position: 'bottom-center'
			});
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

	// Hide events from other side if it's an AI scenario
	// TODO: do this elsewhere
	$effect(() => {
		if (lockedSide) {
			untrack(() => {
				const filteredEventNodes = $nodesStore.map((node) => {
					if (node.type === 'event' && node.side && node.side !== userSideId) {
						node.text = $t('event.eventHidden');
						node.title = $t('event.eventHidden');
						node.author = $t('event.eventHidden');
						node.type = 'hidden';
					}
					return node;
				});
				nodesStore.set(filteredEventNodes);
				linksStore.set(buildLinks(filteredEventNodes));
			});
		}
	});
	onMount(async () => {
		await init();
		prologueSeen = new URL(location.href).searchParams.get('prologueSeen') === 'true';
		userSideId = localStorage.getItem('side_' + sessionData.id);
		if (scenario?.ai && iaConnected && userSideId) {
			lockedSide = true;
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
		{#if prologueSeen}
			<GraphUi bind:session={sessionData} {admin} {user} {events} {ends} {sides} {iaConnected} />
			<MainGraph sessionId={sessionData.id} {sides} {iaConnected} />
		{:else}
			<div class=" fixed flex md:m-8 justify-center items-center bg-gray-950/50">
				<div
					class="flex flex-col gap-8 w-5/6 lg:w-2/3 border-gray-100 backdrop-blur-[2px] border p-8 rounded-lg"
				>
					<h1 class="text-2xl font-bold text-center p-0">{$t('scenario.prologue')}</h1>
					<p class="text-balance leading-7 text-gray-300">{scenario?.prologue}</p>
					{#if scenario?.ai && iaConnected}
						<form onsubmit={handleSideSubmit} class="p-4 flex flex-col gap-4 items-center">
							<select class="p-4 border border-gray-100 rounded w-full" bind:value={userSideId}>
								<option disabled value={null} selected>{$t('scenario.chooseSide')}</option>
								{#each sides as side}
									<option
										disabled={lockedSide && !!userSideId && side.id !== userSideId}
										value={side.id}>{side.name}</option
									>
								{/each}
							</select>
							<button
								disabled={lockedSide}
								type="submit"
								class="font-bold border hover:bg-black disabled:opacity-50 border-gray-200 py-2 px-4 rounded"
							>
								{lockedSide ? $t('scenario.sideChosen') : $t('scenario.choose')}
							</button>
						</form>
					{/if}
					<button
						type="button"
						disabled={scenario?.ai && iaConnected && !lockedSide}
						onclick={handlePrologueSeen}
						class="font-bold w-fit self-center border float-end border-gray-200 py-2 px-4 rounded disabled:opacity-50"
					>
						{$t('scenario.start')}
					</button>
				</div>
			</div>
		{/if}
	</div>
{/await}
