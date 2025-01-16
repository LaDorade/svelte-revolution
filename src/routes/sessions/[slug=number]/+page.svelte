<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import { replaceState } from '$app/navigation';
	import { LoaderPinwheel } from 'lucide-svelte';
	import { pb } from '$lib/client/pocketbase';
	import toast from 'svelte-french-toast';
	import { titleStore } from '$stores/titles/index.svelte';
	import { t } from 'svelte-i18n';
	import GraphUi from '$components/graph/GraphUI.svelte';
	import graph1 from '$lib/assets/graphe1.png';
	import { pseudoSchema } from '$lib/zschemas/pseudo.schema';
	import ShowPrologue from '$components/session/ShowPrologue.svelte';
	import { MainGraph as MainGraphClass } from '$stores/graph/Classes/MainGraph.svelte';
	import MainGraph from '$components/graph/MainGraph.svelte';
	import { viewportStore } from '$stores/ui/index.svelte';
	import DebugPane from '$components/admin/DebugPane.svelte';
	import type { LayoutData } from './$types';

	interface Props {
		data: LayoutData;
	}
	let { data }: Props = $props();
	let { events = [], user = null, ends = [], sides, aiConnected = false, scenario } = data;

	let sessionData = $state(data.sessionData);

	let graph: MainGraphClass | null = $state(null);

	// Intro related
	let prologueSeen = $state(false);
	let userSideId: string | null = $state(null);
	let validSide = $derived(!!sides.find((side) => side.id === userSideId)?.id);
	let sideLocked = $state(false);
	let pseudo: string | null = $state(null);
	let validPseudo = $derived(pseudoSchema.safeParse(pseudo).success);
	let pseudoLocked = $state(false);

	// ? wierd hack to make the admin reactive on page reload
	let admin = $derived($page.data.isAdmin as boolean);

	let sessionTitle = $derived.by(() => {
		return (admin ? 'ADMIN - ' : '') + data.sessionData.name;
	});

	let accessToPage = $derived.by(() => {
		return admin || sessionData.completed || (pseudoLocked && sideLocked);
	});

	async function manageSearchParams() {
		const url = new URL(location.href);
		if (admin) {
			url.searchParams.set('admin', admin.toString());
		} else {
			url.searchParams.delete('admin');
		}
		if ((!sideLocked || !pseudoLocked) && !admin) {
			url.searchParams.delete('prologueSeen');
		}
		prologueSeen = new URL(location.href).searchParams.get('prologueSeen') === 'true';

		await tick(); // wait for the router to be ready
		replaceState(url.toString(), '');
	}

	onMount(async () => {
		titleStore.setNavTitle(sessionTitle);
		if (scenario?.ai && aiConnected) {
			toast.success($t('ia.connected'), {
				position: 'top-left'
			});
		}
		userSideId = localStorage.getItem('side_' + sessionData.id);
		pseudo = localStorage.getItem('pseudo_' + sessionData.id);
		if (validSide) {
			sideLocked = true;
		}
		if (validPseudo) {
			pseudoLocked = true;
		}
		await manageSearchParams();
		viewportStore.seeDebugPanel = localStorage.getItem('seeDebugPanel') === 'true';
	});
</script>

<svelte:head>
	<title>{sessionTitle}</title>
	<meta content={sessionData.expand?.scenario?.prologue} property="description" />
	<meta content={sessionData.image ? pb.files.getURL(sessionData, sessionData.image) : graph1} property="og:image" />
	<meta content={sessionData.name} property="og:title" />
	<meta content={sessionData.expand?.scenario?.prologue} property="og:description" />
	<meta content="Babel Révolution" property="og:site_name" />
	<meta content={$page.url.href} property="og:url" />
</svelte:head>

{#if (data.isSuperAdmin || data.user?.id === sessionData.author) && viewportStore.seeDebugPanel}
	<DebugPane {graph} session={sessionData} />
{/if}

{#await data.nodesPromise}
	<div class=" w-full h-screen flex justify-center items-center bg-black">
		<LoaderPinwheel color="white" class="w-20 z-50 opacity-100 h-20 loader animate-spin" />
	</div>
{:then nodes}
	<div class="">
		{#if prologueSeen && accessToPage}
			<GraphUi {graph} bind:session={sessionData} {admin} {user} {events} {pseudo} {userSideId} {ends} {sides} />
			<MainGraph bind:graph {admin} {userSideId} ai={scenario?.ai} {nodes} sessionId={sessionData.id} {sides} />
		{:else}
			<ShowPrologue
				{graph}
				bind:userSideId
				bind:sideLocked
				bind:pseudoLocked
				bind:pseudo
				bind:prologueSeen
				{validPseudo}
				{validSide}
				{admin}
				{sides}
				{scenario}
				{sessionData}
			/>
		{/if}
	</div>
{/await}
