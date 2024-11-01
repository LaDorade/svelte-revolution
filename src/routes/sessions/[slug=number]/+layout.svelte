<svelte:options runes={true} />

<script lang="ts">
	import { RefreshCcw } from 'lucide-svelte';

	let { children } = $props();
	let key = $state(0);

	function reload() {
		key += 1;
	}
</script>

<button
	class="absolute z-50 cursor-pointer flex justify-center items-center p-2 border-b border-l top-0 right-0"
	onclick={reload}
>
	<RefreshCcw color="white" />
</button>
{#key key}
	{@render children()}
{/key}
