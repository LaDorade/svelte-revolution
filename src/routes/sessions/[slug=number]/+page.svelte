<script lang="ts">
	import graph1 from '$lib/assets/graphe1.png';
	import toast from 'svelte-french-toast';
	import { t } from 'svelte-i18n';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { LoaderPinwheel } from 'lucide-svelte';
	import { pb } from '$lib/client/pocketbase';
	import { titleStore } from '$stores/titles/index.svelte';
	import { MainGraph as MainGraphClass } from '$stores/graph/Classes/MainGraph.svelte';
	import { viewportStore } from '$stores/ui/index.svelte';
	import { CurrentSessionStore, setCurrentSessionCtx } from '$stores/session.svelte';
	import GraphUi from './GraphUI/GraphUI.svelte';
	import MainGraph from './MainGraph.svelte';
	import ShowPrologue from './GraphUI/ShowPrologue.svelte';
	import DebugPane from '$components/admin/DebugPane.svelte';

	import type { LayoutData } from './$types';

	interface Props {
		data: LayoutData;
	}
	let { data }: Props = $props();

	let {
		ai,
		admin,
		user = null,
		sides,
		scenario,
		session
	} = $derived(data);

	const currentSession = $derived(new CurrentSessionStore(
		pb,
		session,
		scenario,
		admin,
		sides,
		ai.connected
	));

	setCurrentSessionCtx(currentSession);


	let graph: MainGraphClass | null = $state(null);

	let sessionTitle = $derived((admin ? 'ADMIN - ' : '') + session.name);

	onMount(async () => {
		titleStore.setNavTitle(sessionTitle);
		
		if (scenario.ai && ai.connected) {
			toast.success($t('ia.connected'), {
				position: 'top-left',
			});
		}

		viewportStore.seeDebugPanel = localStorage.getItem('seeDebugPanel') === 'true';
	});
</script>

<svelte:head>
	<title>{sessionTitle}</title>
	<meta
		content={currentSession.scenario.prologue}
		property="description"
	/>
	<meta
		content={currentSession.session.image
			? pb.files.getURL(currentSession.session, currentSession.session.image)
			: graph1}
		property="og:image"
	/>
	<meta content={currentSession.session.name} property="og:title" />
	<meta
		content={currentSession.scenario.prologue}
		property="og:description"
	/>
	<meta content="Babel Révolution" property="og:site_name" />
	<meta content={page.url.href} property="og:url" />
</svelte:head>

{#if (data.isSuperAdmin || data.user?.id === currentSession.session.author) && viewportStore.seeDebugPanel}
	<DebugPane {graph} />
{/if}

{#await data.nodesPromise}
	<div class=" w-full h-screen flex justify-center items-center bg-black">
		<LoaderPinwheel
			color="white"
			class="w-20 z-50 opacity-100 h-20 loader animate-spin"
		/>
	</div>
{:then nodes}
	<div class="h-full w-full">
		{#if currentSession.userCanAccess && currentSession.userWantAccess}
			<GraphUi {graph} {user} />
			<MainGraph bind:graph {nodes} />
		{:else}
			<ShowPrologue {graph} />
		{/if}
	</div>
{/await}
