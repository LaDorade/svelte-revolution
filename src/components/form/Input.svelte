<script lang="ts">
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

<label class={[
	'text-gray-50',
	'flex flex-col items-start w-full gap-2',
	'bg-black/50 p-4 rounded-lg',
	labelClass
]}>
	{label}
	<input
		class={[
			'ml-2 w-full border-b border-gray-300 focus:border-gray-100 focus:outline-none',
			'text-gray-50 placeholder:text-gray-500'
		]}
		type={type}
		bind:value
		placeholder={placeholder}
		{...rest}
	/>
</label>