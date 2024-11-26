<script lang="ts">
	import { nodesStore } from '$stores/graph';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';
	import type { NodeMessage } from '$types/graph';
	import { fade } from 'svelte/transition';

	let startNode = $derived.by(() => {
		return $nodesStore.find((node) => !node.parent);
	});
	let sortedNodes = $derived.by(() => {
		const map = new Map<string | null, NodeMessage[]>();
		$nodesStore.forEach((node) => {
			if (node.parent) {
				if (map.has(node.parent)) {
					map.get(node.parent)?.push(node);
				} else {
					map.set(node.parent, [node]);
				}
			}
		});
		return map;
	});
</script>

{#snippet leafs(nodes: NodeMessage[], level: number)}
	{#each nodes as node}
		{@const childrens = sortedNodes.get(String(node.id))}
		<li class="flex flex-col gap-2">
			<div class="flex items-center">
				<div class=" text-gray-300 flex items-center">
					{#each Array.from({ length: level - 1 }) as _}
						#
					{/each}
				</div>
				<button
					onclick={() => (mainGraphStore.selectedNode = node)}
					class="border rounded p-1 border-white + {node.id === mainGraphStore.selectedNode?.id
						? 'bg-gray-500'
						: 'bg-gray-800'}"
				>
					{node.title}
				</button>
			</div>
			{#if childrens?.length}
				<ul class=" list-inside list-disc flex flex-col gap-2">
					{@render leafs(childrens, level + 1)}
				</ul>
			{/if}
		</li>
	{/each}
{/snippet}

<div
	in:fade={{ duration: 200 }}
	class="text-gray-100 p-2 flex gap-2 flex-col overflow-y-auto z-50 w-80 h-80 rounded bg-opacity-80 bg-black"
>
	<div class=" text-center">
		{startNode?.title}
	</div>
	{@render leafs(sortedNodes.get(String(startNode?.id ?? '')) ?? [], 1)}
</div>
