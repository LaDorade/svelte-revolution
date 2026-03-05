<script lang="ts">
	import { onNavigate } from '$app/navigation';
	import { type Snippet } from 'svelte';

	onNavigate(() => {
		isOpen = false;
	});

	type Props = {
		triggerClass?: string;
		trigger: Snippet;
		content: Snippet;
	};
	let {
		triggerClass = '',
		trigger,
		content
	}: Props = $props();

	const id = $props.id();

	let isOpen = $state(false);
</script>

<div class="relative">
	<button
		id={id}
		tabindex="0" 
		class="cursor-pointer block {triggerClass}"
		onclick={() => (isOpen = !isOpen)}
	>
		{@render trigger()}
	</button>
	{#if isOpen}
		<div {@attach ((node) => {
			async function handleClickOutside(event: MouseEvent) {
				if (!node.contains(event.target as Node) && !(event.target as Element).closest('#' + id)) {
					isOpen = false;
				}
			}

			document.addEventListener('click', handleClickOutside);
			return () => {
				document.removeEventListener('click', handleClickOutside);
			};
		})} class="absolute z-10 right-0"
		>
			{@render content()}
		</div>
	{/if}
</div>

