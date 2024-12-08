<script lang="ts">
	import { enhance } from '$app/forms';
	import { pb } from '$lib/client/pocketbase';
	import { titleStore } from '$stores/titles/index.svelte';
	import { viewportStore } from '$stores/ui/index.svelte';
	import { locale, locales } from 'svelte-i18n';
	import { t } from 'svelte-i18n';
	import graph1 from '$lib/assets/graphe1.png';
	import nProgress from 'nprogress';
	import type { User } from '$types/pocketBase/TableTypes';

	let { isAdmin, user, seeDebugPanel = $bindable() } = $props();

	function getUserAvatar(user: User) {
		return user.avatar ? pb.files.getUrl(user, user.avatar) : graph1;
	}

	function storePanelInLocalStorage() {
		localStorage.setItem('seeDebugPanel', seeDebugPanel.toString());
	}
</script>

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
				{#if isAdmin}
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
							<li>
								<label>
									{$t('admin.debugPane')}
									<input
										class=" cursor-pointer"
										type="checkbox"
										name="seeDebugPane"
										id="debugPaneCheck"
										onchange={storePanelInLocalStorage}
										bind:checked={seeDebugPanel}
									/>
								</label>
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
	<div class="navbar-end">
		{#if viewportStore.actualBreakpoint !== 'sm'}
			<select bind:value={$locale} class="select select-ghost">
				{#each $locales as loc}
					<option value={loc}>{loc.split('-')[1]}</option>
				{/each}
			</select>
		{/if}
		{#if user}
			<div class="flex-none gap-2">
				<div class="z-50 dropdown dropdown-end">
					<div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
						<div class="w-10 rounded-full">
							<img alt="avatar" src={user ? getUserAvatar(user) : graph1} />
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
								nProgress.start();
								return async ({ update }) => {
									await update({ reset: false });
									nProgress.done();
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
