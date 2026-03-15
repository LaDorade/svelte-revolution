<script lang="ts">
	import { Square, SquareCheck } from 'lucide-svelte';
	import Base from './Base.svelte';
	import { cn } from '$lib/utils';

	import type { HTMLInputAttributes } from 'svelte/elements';

	type Props = HTMLInputAttributes & {
		label: string;
		labelClass?: string;
	}
	let {
		label,
		labelClass,
		checked = $bindable(false),
		...rest
	}: Props = $props();
</script>

<Base {label} labelClass={cn([
	'text-gray-300 hover:text-gray-50',
	'flex flex-row w-full justify-between items-center',
	'cursor-pointer ',
], labelClass)}>
	<div class="flex items-center">
		<span>
			{#if checked}
				<SquareCheck
					strokeWidth="2"
					class="w-4 h-4 stroke-green-500"
				/>
			{:else}
				<Square
					strokeWidth="2"
					class="w-4 h-4 stroke-gray-200"
				/>
			{/if}
		</span>
		<input
			class={[
				'ml-auto',
				'focus:border-gray-100 focus:outline-none',
				'appearance-none'
			]}
			type="checkbox"
			bind:checked
			{...rest}
		/>
	</div>
</Base>