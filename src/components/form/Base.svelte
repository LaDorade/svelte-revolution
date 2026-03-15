<script lang="ts">
	import { cn } from '$lib/utils';
	import type { Snippet } from 'svelte';

	interface Props  {
		label: string | Snippet;
		labelClass?: string;
		children: Snippet;
	}
	let {
		label,
		labelClass,
		children
	}: Props = $props();
</script>

<label class={cn([
	'px-4 py-2',
	'text-gray-50',
	'flex flex-col items-start w-full gap-2',
	'bg-black/50 rounded-lg',
], labelClass)}>
	{#if typeof label === 'string'}
		{label}
	{:else}
		{@render label()}
	{/if}
	{@render children()}
</label>