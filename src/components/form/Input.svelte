<script lang="ts">
	import Base from './Base.svelte';
	import type { HTMLInputAttributes } from 'svelte/elements';

	type Props = HTMLInputAttributes & {
		label: string;
		labelClass?: string;
	}
	let {
		label,
		labelClass,
		value = $bindable(''),
		type = 'text',
		placeholder = '',
		...rest
	}: Props = $props();
</script>

<Base {label} {labelClass}>
	<input
		class={[
			'w-full border-b border-gray-500 focus:border-gray-100 focus:outline-none',
			'text-gray-50 placeholder:text-gray-700',
			'h-full',
			'read-only:bg-transparent read-only:border-gray-700 read-only:text-gray-500',
			'read-only:focus:border-gray-700 read-only:focus:ring-0',
		]}
		type={type}
		bind:value
		placeholder={placeholder}
		{...rest}
	/>
</Base>