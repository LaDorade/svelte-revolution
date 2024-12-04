<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';
	import { LoaderPinwheel } from 'lucide-svelte';
	import { pb } from '$lib/client/pocketbase';
	import { initStores } from './utils';
	import { titleStore } from '$stores/titles/index.svelte';
	import { buildLinks } from '$lib/sessions';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';
	import toast from 'svelte-french-toast';
	import GraphUi from '$components/graph/GraphUI.svelte';
	import MainGraph from '$components/graph/MainGraph.svelte';
	import graph1 from '$lib/assets/graphe1.png';
	import type { PageServerData } from './$types';
	import type { LayoutServerData } from '../../$types';
	import type { Side } from '$types/pocketBase/TableTypes';

	interface Props {
		data: PageServerData & LayoutServerData;
	}
	let { data }: Props = $props();
	let { events = [], user = null, nodesPromise, ends = [], sides, iaConnected = false } = data;

	let sessionData = $state(data.sessionData);

	// ? wierd hack to make the admin reactive on page reload
	let admin = $derived($page.data.isAdmin as boolean);

	let title = $derived.by(() => {
		return (admin ? 'ADMIN - ' : '') + data.sessionData.name;
	});

	function manageUrl() {
		// update query params with admin status
		const url = new URL(location.href);
		if (admin) {
			url.searchParams.set('admin', admin.toString());
			replaceState(url.toString(), '');
		} else {
			url.searchParams.delete('admin');
			replaceState(url.toString(), '');
		}
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
		manageUrl();
		titleStore.setNavTitle(title);

		if (iaConnected) {
			toast.success("L'IA est connectée", {
				position: 'top-left'
			});
		}
	}

	onMount(async () => {
		await init();
	});

	onDestroy(() => {
		mainGraphStore.selectedNode = null;
	});
</script>

<svelte:head>
	<title>{title}</title>
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
	<div class="relative">
		<GraphUi bind:session={sessionData} {admin} {user} {events} {ends} {sides} {iaConnected} />
		<MainGraph sessionId={sessionData.id} {sides} {iaConnected} />
	</div>
{/await}
