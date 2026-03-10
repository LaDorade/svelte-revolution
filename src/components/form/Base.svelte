<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props  {
		label: string;
		labelClass?: string;
		children: Snippet;
	}
	let {
		label,
		labelClass,
		children
	}: Props = $props();
</script>

<label class={[
	'text-gray-50',
	'flex flex-col items-start w-full gap-2',
	'bg-black/50 rounded-lg',
	labelClass,
]}>
	{label}
	{@render children()}
</label>