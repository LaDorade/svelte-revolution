<script lang="ts">
	import type { Snippet } from 'svelte';

	type Props = {
		onclick?: () => void;
		href?: string;
		variant: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'link';
		children: string | Snippet;
		class?: string;
	}
	let { onclick, href, variant, children, class: className }: Props = $props();

	function getVariantClasses() {
		switch (variant) {
		case 'primary':
			return 'bg-primary-500 hover:bg-primary-600 text-black';
		case 'secondary':
			return 'bg-secondary-300 text-white hover:bg-secondary-200';
		case 'ghost':
			return 'bg-transparent text-gray-300 hover:bg-gray-700';
		case 'link':
			return 'bg-transparent text-blue-500 hover:underline';
		case 'tertiary':
			return 'bg-white text-black hover:bg-white/90';
		default: {
			console.warn(`Unknown button variant: ${variant satisfies never}`);
			return variant;
		}
		}
	}
</script>

{#if href}
	<a {href}
		class={[
			'h-fit w-full cursor-pointer',
			'text-center text-nowrap w-full',
			'px-4 py-2 rounded-lg transition-colors duration-200',
			getVariantClasses(),
			className
		]}
	>
		{#if typeof children === 'string'}
			{children}
		{:else}
			{@render children()}
		{/if}
	</a>
{:else}
	<button
		onclick={onclick}
		class={[
			'h-fit w-full cursor-pointer',
			'text-center text-nowrap w-full',
			'px-4 py-2 rounded-lg transition-colors duration-200',
			getVariantClasses(),
			className
		]}
	>
		{#if typeof children === 'string'}
			{children}
		{:else}
			{@render children()}
		{/if}
	</button>
{/if}