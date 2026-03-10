<script lang="ts">
	import { t } from 'svelte-i18n';
	import Overlay from './Overlay.svelte';
	import { fade } from 'svelte/transition';

	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { Side } from '$types/pocketBase/TableTypes';
	import type { MyPocketBase } from '$types/pocketBase';
	import Audio from './Audio.svelte';


	interface Props {
		pb: MyPocketBase;
		graph: MainGraph | null;
		sides: Side[];
	}
	let {
		pb,
		graph,
		sides
	}: Props = $props();

	let side = $derived(sides.find((side) => side.id === graph?.selectedNode?.side) || null);
</script>

<Overlay>
	<div class={[
		'flex flex-col items-start gap-2 cursor-default p-2 text-sm',
		'max-w-80 max-h-96'
	]}
		in:fade={{ duration: 150 }}
	>
		{#if graph?.selectedNode}
			{#key graph?.selectedNode}
				<div
					class="text-lg text-gray-50 first-letter:capitalize"
				>
					{graph?.selectedNode.title}
				</div>
				{#if side}
					<div class="text-green-400 flex items-center">
						<svg
							class="w-4 h-4 mr-1"
							viewBox="-12 -12 24 24"
						>
							<path
								d={side?.icon}
								fill="rgb(74 222 128)"
							/>
						</svg>
						{side?.name}
					</div>
				{/if}
				<div>
					{$t('inSession.from')}
					<span class="text-white"
					>{graph?.selectedNode.author}</span
					>
				</div>
				<div
					class="max-h-60 overflow-auto text-pretty text-gray-300"
				>
					<!-- eslint-disable-next-line svelte/no-at-html-tags-->
					{@html graph?.selectedNode.text}
				</div>
				{#if graph?.selectedNode.audio}
					<Audio audioPath={pb.files.getURL(
						graph?.selectedNode,
						graph?.selectedNode.audio as string,
					)} />
				{/if}
			{/key}
		{:else}
			<div
				class="text-lg first-letter:capitalize"
			>
				{$t('inSession.noNodeSelected')}
			</div>
		{/if}
	</div>
</Overlay>