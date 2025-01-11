<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { RefreshCcw } from 'lucide-svelte';

	let { children } = $props();
	let key = $state(0);

	async function reload() {
		await invalidateAll();
		key += 1;
	}
</script>

<button
	class="absolute print:hidden z-40 m-4 cursor-pointer flex justify-center items-center p-2 border rounded-full top-0 right-0"
	onclick={reload}
>
	<RefreshCcw strokeWidth={1.5} color="white" />
</button>
{#key key}
	{@render children()}
{/key}
