<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children: Snippet;
	}
	let {
		children
	}: Props = $props();
</script>

<div
	class={[
		'fixed overflow-y-auto z-40 rounded-xl shadow-2xl',
		'p-2 m-4 bottom-0 left-0 bg-black min-w-0 flex',
	]}
>
	{@render children()}
</div>