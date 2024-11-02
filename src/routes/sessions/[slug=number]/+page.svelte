<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';
	import { pb } from '$lib/client/pocketbase';
	import { initStores } from './utils';
	import GraphUi from '$components/graph/GraphUI.svelte';
	import MainGraph from '$components/graph/MainGraph.svelte';
	import Watermark from '$components/admin/Watermark.svelte';
	import graph1 from '$lib/assets/graphe1.png';
	import type { PageServerData } from './$types';
	import type { LayoutServerData } from '../../$types';
	import { titleStore } from '$stores/titles/index.svelte';
	import { selectedNodeStore } from '$stores/graph';
	import toast from 'svelte-french-toast';

	interface Props {
		data: PageServerData & LayoutServerData;
	}
	let { data }: Props = $props();
	let { events = [], user = null, nodesAndLinks, ends = [], sides = [], isAdmin = false, iaConnected = false } = data;

	let sessionData = $state(data.sessionData);

	let admin = $derived($page.data.isAdmin as boolean);

	let title = $derived.by(() => {
		return (admin ? 'ADMIN - ' : '') + data.sessionData.name;
	});

	initStores(nodesAndLinks.nodes, nodesAndLinks.links);

	onMount(async () => {
		// Listen for session completion
		await pb.collection('Session').subscribe(data.sessionData.id, async (res) => {
			if (!res.record || !res.record.completed) return;
			try {
				sessionData.completed = res.record.completed;
				const end = await pb.collection('End').getOne(res.record.end ?? '');
				sessionData.expand = sessionData.expand
					? {
							...sessionData.expand,
							...end
						}
					: {};
			} catch (e) {
				console.error(e);
			}
		});
		// update query params with admin status
		const url = new URL(location.href);
		if (admin) {
			url.searchParams.set('admin', admin.toString());
			replaceState(url.toString(), '');
		} else {
			url.searchParams.delete('admin');
			replaceState(url.toString(), '');
		}

		titleStore.setNavTitle(title);

		if (iaConnected) {
			toast.success("L'IA est connectée", {
				position: 'top-left'
			});
		}
	});

	onDestroy(() => {
		selectedNodeStore.set(null);
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

<div class="relative">
	{#if admin && user}
		<GraphUi {admin} session={sessionData} {user} {events} {ends} {sides} />
		<Watermark watermarkText="Admin">
			<MainGraph sessionId={sessionData.id} />
		</Watermark>
	{:else}
		<GraphUi session={sessionData} {sides} />
		<MainGraph sessionId={sessionData.id} />
	{/if}
</div>
