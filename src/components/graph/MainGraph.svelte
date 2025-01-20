<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { pb } from '$lib/client/pocketbase';
	import { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { NodeMessage } from '$types/graph';
	import type { GraphNode, Side } from '$types/pocketBase/TableTypes';

	// Dev Feature to reinstanciate the component when the file is changed
	// ? It's because the hot reload is not working well with the d3 library
	if (import.meta.hot) {
		import.meta.hot.accept(() => {
			import.meta.hot?.invalidate();
		});
	}

	interface Props {
		admin: boolean;
		nodes: GraphNode[];
		sessionId: string;
		sides: Side[];
		iaConnected?: boolean;
		graph: MainGraph | null;
		ai: boolean | undefined;
		userSideId: string | number | null;
	}
	let { nodes, sessionId, sides, iaConnected, userSideId, admin, ai, graph = $bindable() }: Props = $props();

	let svg: SVGElement | null = $state(null);

	function updateSVGSize() {
		if (svg) {
			svg.setAttribute('width', window.innerWidth.toString());
			svg.setAttribute('height', window.innerHeight.toString());
		}
	}

	const realTimeActions = {
		create: (record: NodeMessage) => {
			if (!admin && iaConnected && record?.type === 'event' && record.side) {
				const userSide = localStorage.getItem('side_' + sessionId);
				if (userSide !== record.side) {
					return;
				}
			}
			graph?.addNode(record);
		},
		update: (record: NodeMessage) => {
			graph?.updateNode(record);
		},
		delete: async (record: GraphNode) => {
			graph?.deleteNode(record);
		}
	};

	async function realTimeNodeUpdate() {
		// Real-time connection to the database
		await pb.collection('Node').subscribe(
			'*',
			async ({ action, record }) => {
				if (action !== 'delete' && action !== 'create' && action !== 'update') return;
				await realTimeActions[action](record);
			},
			{
				filter: `session="${sessionId}"`
			}
		);
	}

	onMount(async () => {
		if (!svg) return;

		updateSVGSize();
		window.addEventListener('resize', updateSVGSize);

		graph = new MainGraph(svg, nodes, sides, {
			width: window.innerWidth,
			height: window.innerHeight
		});
		if (ai && !admin) {
			graph.filterNodeBySide(userSideId);
		}
		await realTimeNodeUpdate();
	});

	onDestroy(() => {
		if (graph) {
			graph._simulation.stop();
			graph.selectedNode = null;
		}
		pb.collection('Node').unsubscribe();
		window.removeEventListener('resize', updateSVGSize);
	});
</script>

<svelte:window
	on:resize={() =>
		graph?.setOptions({
			width: window.innerWidth,
			height: window.innerHeight
		})}
/>

<svg 
	bind:this={svg} 
	class="bg-black z-10 cursor-grab bg-dotted-40 bg-dotted-gray">
</svg>
