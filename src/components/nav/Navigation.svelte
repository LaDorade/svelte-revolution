<script lang="ts">
	import { pb } from '$lib/client/pocketbase';
	import { titleStore } from '$stores/titles/index.svelte';
	import { viewportStore } from '$stores/ui/index.svelte';
	import { locale, locales } from 'svelte-i18n';
	import { t } from 'svelte-i18n';
	import graph1 from '$lib/assets/graphe1.png';
	import type { User } from '$types/pocketBase/TableTypes';
	import { goto, invalidateAll } from '$app/navigation';
	import nProgress from 'nprogress';
	import { resolve } from '$app/paths';
	import { Menu } from 'lucide-svelte';
	import Dropdown from '$components/Dropdown.svelte';
	import Button from '$components/Button.svelte';
	import { SvelteSet } from 'svelte/reactivity';

	let { isAdmin, user } = $props();

	function getUserAvatar(user: User) {
		return user.avatar ? pb.files.getURL(user, user.avatar) : graph1;
	}

	async function logout() {
		nProgress.start();
		pb.authStore.clear();
		await invalidateAll();
		nProgress.done();
		goto(resolve('/'));
	}

	const navItems = new SvelteSet([
		{ label: $t('nav.home'), href: resolve('/') },
		{ label: $t('nav.sessions'), href: resolve('/sessions') }
	]);
	const adminNavItems = new SvelteSet([
		{ label: $t('admin.administration'), href: resolve('/admin') },
		{ label: $t('admin.scenario.createScenario'), href: resolve('/admin/scenario/create') },
		{ label: $t('admin.session.createSession'), href: resolve('/admin/sessions/create') }
	]);
</script>

<nav class={[
	'print:hidden z-50 border-b border-gray-500 bg-black text-gray-200 bg-opacity-70',
	'flex items-center'
]}>
	<div class="flex gap-4 items-center p-4">
		<Dropdown>
			{#snippet trigger()}
				<Menu class="h-fit w-fit" />
			{/snippet}
			{#snippet content()}
				<ul
					class={[
						'flex flex-col gap-4 w-fit',
						'rounded-lg overflow-hidden',
						'z-10 p-4 bg-secondary-300 shadow',
						'absolute'
					]}
				>
					{#each navItems as item (item.href)}
						<li class="w-full">
							<Button
								class="p-2 w-full"
								variant="secondary"
								href={item.href}
							>
								{item.label}
							</Button>
						</li>
					{/each}
					{#if isAdmin}
						<span class="w-full border-b border-secondary-100"></span>
						{#each adminNavItems as item, i (item.href)}
							<li class="w-full">
								<Button
									class={i === 0 ? 'pl-2' : 'pl-4'}
									variant="secondary"
									href={item.href}
								>
									{item.label}
								</Button>
							</li>
						{/each}
					{/if}
					{#if viewportStore.actualBreakpoint === 'sm'}
						<select bind:value={$locale} class="select select-ghost">
							{#each $locales as loc (loc)}
								<option class="uppercase" value={loc}>{loc.split('-')[0]}</option>
							{/each}
						</select>
					{/if}
				</ul>
			{/snippet}
		</Dropdown>
		<a href={resolve('/')} class="font-bold font-alterType">{titleStore.navTitle}</a>
	</div>
	<div class="ml-auto flex p-2 gap-4">
		{#if viewportStore.actualBreakpoint !== 'sm'}
			<select bind:value={$locale} class={[
				'cursor-pointer',
				'border rounded-lg p-2 border-gray-500 bg-black',
				''
			]}>
				{#each $locales as loc (loc)}
					<option class="cursor-pointer" value={loc}>{loc.split('-')[0]}</option>
				{/each}
			</select>
		{/if}
		{#if user}
			<Dropdown triggerClass="flex items-center justify-center h-full">
				{#snippet trigger()}
					<div class="max-w-10 flex rounded-full">
						<img alt="avatar" src={user ? getUserAvatar(user) : graph1} />
					</div>
				{/snippet}
				{#snippet content()}
					<div class="z-10 bg-secondary-300 rounded-lg flex flex-col gap-2">
						<Button
							variant="secondary"
							onclick={logout}
						>
							{$t('nav.logout')}
						</Button>
					</div>
				{/snippet}
			</Dropdown>
		{:else}
			<Button 
				href={resolve('/login')} 
				class=""
				variant="ghost"
			>
				{$t('admin.administration')}
			</Button>
		{/if}
	</div>
</nav>
