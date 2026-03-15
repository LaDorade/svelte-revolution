<script lang="ts">
	import * as Select from '$lib/components/ui/select/index.js';
	import Base from './Base.svelte';

	interface Props {
		triggerClass?: string;
		contentClass?: string;
		label: string;
		value: string;
		groups?: string[];
		values: {
			value: string;
			label: string;
			group?: string;
		}[];
	}

	let {
		triggerClass,
		contentClass,
		label,
		groups,
		values,
		value = $bindable(''),
	}: Props = $props();

	const triggerContent = $derived(
		values.find((f) => f.value === value)?.label ?? label
	);
</script>

<Base {label}>
	<Select.Root type="single" bind:value>
		<Select.Trigger class={[
			'cursor-pointer',
			'rounded-lg border-none p-0',
			value ? 'text-gray-50' : 'text-gray-400',
			triggerClass
		]}>
			{triggerContent}
		</Select.Trigger>
		<Select.Content class=" bg-black {contentClass}">
			{#if groups && groups.length > 0}
				{#each groups as group (group)}
					<Select.Group>
						<Select.Label class="px-2 py-1 text-sm text-gray-400">
							{group}
						</Select.Label>
						{#each values.filter((v) => v.group === group) as option (option.value)}
							<Select.Item value={option.value}>
								{option.label}
							</Select.Item>
						{/each}
					</Select.Group>
				{/each}
			{:else}
				{#each values as option (option.value)}
					<Select.Item value={option.value}>
						{option.label}
					</Select.Item>
				{/each}
			{/if}
		</Select.Content>
	</Select.Root>
</Base>