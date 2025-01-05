<script lang="ts">
	import '../app.css';
	import { onMount, untrack, type Snippet } from 'svelte';
	import { navigating, page } from '$app/stores';
	import NProgress from 'nprogress';
	import { Toaster } from 'svelte-french-toast';
	import { t } from 'svelte-i18n';
	import 'nprogress/nprogress.css';
	import graph1 from '$lib/assets/graphe1.png';
	import { viewportStore } from '$stores/ui/index.svelte';
	import type { User } from '$types/pocketBase/TableTypes';
	import DebugPane from '$components/admin/DebugPane.svelte';
	import BackToTop from '$components/BackToTop.svelte';
	import Navigation from '$components/nav/Navigation.svelte';

	type Props = {
		data: { user: User; isAdmin: boolean };
		children: Snippet;
	};
	let { data, children }: Props = $props();

	NProgress.configure({
		minimum: 0.16
	});

	$effect.pre(() => {
		if ($navigating) {
			NProgress.start();
		} else {
			NProgress.done();
		}
	});

	onMount(() => {
		viewportStore.updateViewport(window);
		viewportStore.seeDebugPanel = localStorage.getItem('seeDebugPanel') === 'true';
	});
</script>

<svelte:head>
	<title>Babel Révolution</title>
	<meta name="description" content={$t('home.intro')} />
	<meta property="og:image" content={graph1} />
	<meta property="og:title" content="Babel Révolution" />
	<meta property="og:description" content={$t('home.intro')} />
	<meta property="og:site_name" content="Babel Révolution" />
	<meta property="og:url" content={$page.url.href} />
</svelte:head>

<svelte:window on:resize={() => viewportStore.updateViewport(window)} />

<!-- Utilities -->
<Toaster />
<BackToTop />

<Navigation isAdmin={data.isAdmin} user={data.user} />

<!-- MAIN -->
<div class="relative inset-0 w-full h-full text-gray-300">
	{@render children()}
	<div
		class="absolute top-0 left-0 -z-50 bg-dark-800 opacity-90 h-full w-full bg-dotted-gray bg-dotted-40
	[mask-image:radial-gradient(ellipse_60%_70%_at_50%_50%,#000_40%,transparent_100%)]"
	></div>
</div>
