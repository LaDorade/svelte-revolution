<script lang="ts">
	import { fade } from 'svelte/transition';
	import { t } from 'svelte-i18n';
	import { SvelteMap, SvelteURL } from 'svelte/reactivity';
	import { resolve } from '$app/paths';
	import type { NodeMessage } from '$types/graph';
	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { GraphNode } from '$types/pocketBase/TableTypes';

	let { graph }: { graph: MainGraph | null } = $props();

	let sortedNodes = $derived.by(() => {
		const map = new SvelteMap<string | null, GraphNode[]>();
		graph?._nodes.forEach((node) => {
			if (map.has(node.parent)) {
				map.get(node.parent)?.push(node);
			} else {
				map.set(node.parent, [node]);
			}
		});
		return map;
	});

	const constructPrintUrl = (): ReturnType<typeof resolve> => {
		const url = new SvelteURL(window.location.href);
		url.pathname += '/print';
		return url.toString() as ReturnType<typeof resolve>;
	};
</script>

{#snippet leafs(nodes: NodeMessage[], level: number)}
	{#each nodes as node (node.id)}
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
	<!-- eslint-disable-next-line svelte/no-navigation-without-resolve-->
	<a class="sticky -bottom-2 bg-black w-full p-4 text-gray-200 hover:text-white" href={constructPrintUrl()}>
		&gt {$t('print.print')}
	</a>
</div>
