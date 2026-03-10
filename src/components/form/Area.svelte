<script lang="ts">
	import Base from './Base.svelte';

	import type { HTMLTextareaAttributes } from 'svelte/elements';

	type Props = HTMLTextareaAttributes & {
		label: string;
		labelClass?: string;
	}
	let {
		label,
		labelClass,
		value = $bindable(''),
		placeholder = '',
		...rest
	}: Props = $props();
</script>

<Base {label} {labelClass}>
	<textarea
		class={[
			'w-full border-b border-gray-500 focus:border-gray-100 focus:outline-none',
			'text-gray-50 placeholder:text-gray-700',
			'min-h-10 max-h-28'
		]}
		bind:value
		placeholder={placeholder}
		{...rest}
	>
	</textarea>
</Base>