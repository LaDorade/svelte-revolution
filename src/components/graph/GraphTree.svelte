<script lang="ts">
	import { fade } from 'svelte/transition';
	import type { NodeMessage } from '$types/graph';
	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { GraphNode } from '$types/pocketBase/TableTypes';
	import { t } from 'svelte-i18n';

	let { graph }: { graph: MainGraph | null } = $props();

	let sortedNodes = $derived.by(() => {
		const map = new Map<string | null, GraphNode[]>();
		graph?._nodes.forEach((node) => {
			if (map.has(node.parent)) {
				map.get(node.parent)?.push(node);
			} else {
				map.set(node.parent, [node]);
			}
		});
		return map;
	});

	const constructPrintUrl = () => {
		const url = new URL(window.location.href);
		url.pathname += '/print';
		return url.toString();
	};
</script>

{#snippet leafs(nodes: NodeMessage[], level: number)}
	{#each nodes as node}
		{@const childrens = sortedNodes.get(String(node.id))}
		<div class="border-l p-1 pr-0 m-1 mr-0">
			<button
				class={graph?.selectedNode === node ? 'text-primary-500' : ''}
				onclick={() => {
					if (graph) {
						graph.selectedNode = node;
					}
				}}
			>
				{node.title}
			</button>
			{#if childrens?.length}
				<div class="ml-2">
					{@render leafs(childrens, level + 1)}
				</div>
			{/if}
		</div>
	{/each}
{/snippet}

<div
	in:fade={{ duration: 200 }}
	class="text-gray-100 m-2 p-2 border flex gap-2 flex-col overflow-y-auto z-50 w-80 h-80 rounded bg-black/90"
>
	{@render leafs(graph?._nodes.filter((node) => !node.parent) ?? [], 1)}
	<a class="sticky -bottom-2 bg-black w-full p-4 text-gray-200 hover:text-white" href={constructPrintUrl()}>
		{$t('print.print')}
	</a>
</div>
