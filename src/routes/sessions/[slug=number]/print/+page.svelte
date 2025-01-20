<script lang="ts">
	import type { NodeMessage } from '$types/graph';
	import { t } from 'svelte-i18n';
	import type { PageData } from '../print/$types';

	interface Props {
		data: PageData;
	}
	let { data }: Props = $props();

	let sortedNodes = $derived.by(() => {
		const map = new Map<string | null, NodeMessage[]>();
		const nodes = data.nodes;
		nodes.forEach((node) => {
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

<div class="print-container w-full h-screen overflow-hidden flex flex-col gap-4 p-5 box-border">
	<h1 class="print:hidden title text-center text-2xl font-bold">
		{$t('print.printTitle')}
	</h1>
	<div class="print:hidden flex justify-between gap-4">
		<button class="rounded-xl text-black duration-75 bg-white p-4 hover:bg-gray-200" onclick={() => window.print()}>
			{$t('print.print')}
		</button>
		<button
			class="rounded-xl text-gray-50 duration-75 bg-gray-700 hover:bg-gray-400 p-4"
			onclick={() => (window.location.href = window.location.href.replace('/print', ''))}
		>
			{$t('print.returnToGraph')}
		</button>
	</div>
	<div class=" hidden print:block sticky top-0 z-50 text-black">
		<h1 class="text-xl font-bold text-center">BⱯBEL RËVOLUㅏION</h1>
		<h2 class="text-lg font-bold text-center">
			{$t('sessions.session')} :
			{data.sessionData.name}
		</h2>
	</div>
	<div class="print:text-black content flex-1 overflow-y-auto">
		{@render leafs(
			data.nodes.filter((node) => !node.parent),
			1
		)}
	</div>
</div>

{#snippet leafs(nodes: NodeMessage[], level: number)}
	{#each nodes as node}
		{@const childrens = sortedNodes.get(String(node.id))}
		<div class="node border-l p-1 pr-0 m-1 mr-0 bg-black">
			<div class="pr-2">
				{node.title}
				<div class=" text-xs text-gray-400">
					{node.text}
				</div>
			</div>
			{#if childrens?.length}
				<div class="children ml-2">
					{@render leafs(childrens, level + 1)}
				</div>
			{/if}
		</div>
	{/each}
{/snippet}
