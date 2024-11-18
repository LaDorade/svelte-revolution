<script lang="ts">
	import type { Snippet } from 'svelte';
	// TODO: animate the hover
	type Props = {
		children: Snippet;
	};
	let { children }: Props = $props();
</script>

<div>
	{@render children()}
</div>
