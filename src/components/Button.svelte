<script lang="ts">
	import { cn } from '$lib/utils';
	import type { Snippet } from 'svelte';
	import type { HTMLAnchorAttributes, HTMLButtonAttributes } from 'svelte/elements';

	type Props = (HTMLButtonAttributes| HTMLAnchorAttributes) & {
		children: string | Snippet;
		variant: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'link';
	};
	let {
		variant,
		children,
		class: className,
		...rest
	}: Props = $props();

	function getVariantClasses() {
		switch (variant) {
		case 'primary':
			return 'bg-primary-500 hover:bg-primary-600 text-black';
		case 'secondary':
			return 'bg-secondary-300 text-white hover:bg-secondary-200';
		case 'ghost':
			return 'bg-transparent text-gray-300 hover:bg-gray-800 border border-gray-500 hover:border-gray-500 disabled:bg-gray-900/20 disabled:border-gray-700 disabled:text-gray-500';
		case 'link':
			return 'bg-transparent text-blue-500 hover:underline';
		case 'tertiary':
			return 'bg-white text-black hover:bg-white/90';
		default: {
			console.warn(
				`Unknown button variant: ${variant satisfies never}`,
			);
			return variant;
		}
		}
	}
</script>

{#if 'href' in rest}
	<a
		{...rest}
		class={cn([
			'h-fit cursor-pointer',
			'text-center text-nowrap',
			'px-4 py-2 rounded-lg transition-colors duration-200',
			getVariantClasses(),
		], className)}
	>
		{#if typeof children === 'string'}
			{children}
		{:else}
			{@render children()}
		{/if}
	</a>
{:else}
	<button
		{...rest as HTMLButtonAttributes}
		class={cn([
			'h-fit cursor-pointer',
			'text-center text-nowrap',
			'px-4 py-2 rounded-lg transition-colors duration-200',
			'disabled:bg-gray-600 disabled:text-gray-400 disabled:cursor-not-allowed',
		], getVariantClasses(), className)}
	>
		{#if typeof children === 'string'}
			{children}
		{:else}
			{@render children()}
		{/if}
	</button>
{/if}
