<script lang="ts">
	import { t } from 'svelte-i18n';
	import { titleStore } from '$stores/titles/index.svelte.js';
	import { onDestroy, onMount, type Snippet } from 'svelte';
	import { resolve } from '$app/paths';
	import type { LayoutData } from './$types.js';

	interface Props {
		data: LayoutData;
		children: Snippet;
	}
	let { data, children }: Props = $props();

	let activeTab = $derived(data?.route);

	const tabs = [
		{ href: '/admin/scenario/create', label: $t('admin.scenario.createScenario') },
		{ href: '/admin/sessions/create', label: $t('admin.session.createSession') },
		{ href: '/admin/user/create', label: $t('admin.user.createUser') }
	] as const;

	onMount(() => {
		titleStore.setNavTitle('Admin');
	});
	onDestroy(() => {
		titleStore.setNavTitle('Babel Revolution');
	});
</script>

<div class="flex flex-col items-center gap-4 py-4">
	<a href={resolve('/admin')} class="text-4xl font-thin text-center text-white hover:text-green-500 first-letter:capitalize">
		{$t('admin.administration')}
	</a>
	<div role="tablist" class="tabs tabs-lifted">
		{#each tabs.filter(tab => tab.href !== '/admin/user/create' || data.user?.role === 'superAdmin') as tab (tab.href)}
			<a
				href={resolve(tab.href)}
				role="tab"
				class="tab hover:text-primary-500 {activeTab === tab.href ? 'tab-active' : 'text-white'}"
			>
				{tab.label}
			</a>
		{/each}
	</div>
</div>

{@render children()}
