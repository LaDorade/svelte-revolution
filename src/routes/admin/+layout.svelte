<script lang="ts">
	import { t } from 'svelte-i18n';
	import { titleStore } from '$stores/titles/index.svelte.js';
	import { onDestroy, onMount, type Snippet } from 'svelte';
	import type { LayoutData } from './$types.js';

	interface Props {
		data: LayoutData;
		children: Snippet;
	}
	let { data, children }: Props = $props();

	let activeTab = $derived(data?.route);

	const tabs = [
		{ href: '/admin/scenario/create', label: $t('admin.scenario.createScenario') },
		{ href: '/admin/sessions/create', label: $t('admin.session.createSession') }
	];
	if (data.user?.role === 'superAdmin') {
		tabs.push({ href: '/admin/user/create', label: $t('admin.user.createUser') });
	}

	onMount(() => {
		titleStore.setNavTitle('Admin');
	});
	onDestroy(() => {
		titleStore.setNavTitle('Babel Revolution');
	});
</script>

<div class="flex flex-col items-center gap-4 py-4">
	<a href="/admin" class="text-4xl font-thin text-center text-white hover:text-green-500 first-letter:capitalize">
		{$t('admin.administration')}
	</a>
	<div role="tablist" class="tabs tabs-lifted">
		{#each tabs as tab}
			<a
				href={tab.href}
				role="tab"
				class="tab hover:text-green-500 {activeTab === tab.href ? 'tab-active' : 'text-white'}"
			>
				{tab.label}
			</a>
		{/each}
	</div>
</div>

{@render children()}
