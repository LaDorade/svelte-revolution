<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
		tooltip: Snippet;
	}
	let { children, tooltip }: Props = $props();

	let tooltipVisible = $state(false);
</script>

<div
	class="h-full w-full"
	role="tooltip"
	onmouseenter={() => (tooltipVisible = true)}
	onmouseleave={() => (tooltipVisible = false)}
>
	{@render children()}
	{#if tooltipVisible}
		{@render tooltip()}
	{/if}
</div>
