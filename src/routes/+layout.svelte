<script lang="ts">
	import '../app.css';
	import { onMount, type Snippet } from 'svelte';
	import { navigating, page } from '$app/stores';
	import { enhance } from '$app/forms';
	import NProgress from 'nprogress';
	import { Toaster } from 'svelte-french-toast';
	import { locale, locales, t } from 'svelte-i18n';
	import 'nprogress/nprogress.css';
	import graph1 from '$lib/assets/graphe1.png';
	import { viewportStore } from '$stores/ui/index.svelte';
	import { titleStore } from '$stores/titles/index.svelte';
	import type { User } from '$types/pocketBase/TableTypes';
	import DebugPane from '$components/admin/DebugPane.svelte';
	import BackToTop from '$components/BackToTop.svelte';
	import { pb } from '$lib/client/pocketbase';

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

	function getUserAvatar(user: User) {
		return user.avatar ? pb.files.getUrl(user, user.avatar) : graph1;
	}

	onMount(() => {
		viewportStore.updateViewport(window);
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
{#if $page.data.user?.role === 'superAdmin'}
	<DebugPane />
{/if}

<!-- NAV -->
<nav class="sticky top-0 z-50 border-b border-gray-500 bg-black navbar text-gray-200 bg-opacity-30">
	<div class="navbar-start">
		<div class="dropdown">
			<button tabindex="0" aria-label="menu" class="btn btn-ghost">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-5 h-5"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
				</svg>
			</button>
			<ul
				role="menu"
				tabindex="0"
				class="z-50 p-2 mt-3 bg-gray-800 shadow menu dropdown-content rounded-box w-52"
			>
				<li><a href="/">{$t('nav.home')}</a></li>
				<li><a href="/sessions">{$t('nav.sessions')}</a></li>
				{#if data.isAdmin}
					<li>
						<a href="/admin">{$t('nav.admin')}</a>
						<ul class="p-2">
							<li>
								<a href="/admin">{$t('sessions.yourSessions')}</a>
							</li>
							<li>
								<a href="/admin/scenario/create">{$t('scenario.createScenario')}</a>
							</li>
							<li>
								<a class="text-nowrap" href="/admin/sessions/create">{$t('sessions.createSession')}</a>
							</li>
						</ul>
					</li>
				{/if}
				{#if viewportStore.actualBreakpoint === 'sm'}
					<select bind:value={$locale} class="select select-ghost">
						{#each $locales as loc}
							<option class="uppercase" value={loc}>{loc.split('-')[0]}</option>
						{/each}
					</select>
				{/if}
			</ul>
		</div>
		<a href="/" class="text-xl btn btn-ghost">{titleStore.navTitle}</a>
	</div>
	<div class=" navbar-end">
		{#if viewportStore.actualBreakpoint !== 'sm'}
			<select bind:value={$locale} class="select select-ghost">
				{#each $locales as loc}
					<option value={loc}>{loc.split('-')[1]}</option>
				{/each}
			</select>
		{/if}
		{#if data.user}
			<div class="flex-none gap-2">
				<div class="z-50 dropdown dropdown-end">
					<div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
						<div class="w-10 rounded-full">
							<img alt="avatar" src={data.user ? getUserAvatar(data.user) : graph1} />
						</div>
					</div>
					<ul
						tabindex="0"
						role="menu"
						class="z-40 p-2 mt-3 bg-gray-800 shadow menu menu-sm dropdown-content rounded-box w-52"
					>
						<li class="text-gray-500">
							<a href="/" class="justify-between">
								{$t('nav.profile')}
								<span class="badge">{$t('soon')}</span>
							</a>
						</li>
						<li class="text-gray-500">
							<a href="/"
								>{$t('nav.settings')}
								<span class="badge">{$t('soon')}</span>
							</a>
						</li>
						<form
							action="/logout?/logout"
							use:enhance={() => {
								NProgress.start();
								return async ({ update }) => {
									await update({ reset: false });
									NProgress.done();
								};
							}}
							onsubmit={(e) => e.preventDefault()}
							method="post"
						>
							<button class="z-50 w-full" type="submit">{$t('nav.logout')}</button>
						</form>
					</ul>
				</div>
			</div>
		{:else}
			<a href="/login" class="justify-between btn btn-ghost">{$t('admin')}</a>
		{/if}
	</div>
</nav>

<!-- MAIN -->
<div class="relative inset-0 w-full h-full text-gray-300">
	{@render children()}
	<div
		class="absolute top-0 left-0 -z-50 bg-green-950 opacity-90 h-full w-full bg-dotted-lightGray bg-dotted-40
	[mask-image:radial-gradient(ellipse_60%_70%_at_50%_50%,#000_40%,transparent_100%)]"
	></div>
</div>
