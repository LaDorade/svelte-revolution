<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { pb } from '$lib/client/pocketbase';
	import { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import { getCurrentSessionCtx } from '$stores/session.svelte';
	import type { NodeMessage } from '$types/graph';
	import type { GraphNode } from '$types/pocketBase/TableTypes';

	// Dev Feature to reinstanciate the component when the file is changed
	// ? It's because the hot reload is not working well with the d3 library
	if (import.meta.hot) {
		import.meta.hot.accept(() => {
			import.meta.hot?.invalidate();
		});
	}

	interface Props {
		nodes: GraphNode[];
		graph: MainGraph | null;
	}
	let {
		nodes,
		graph = $bindable()
	}: Props = $props();

	let svg: SVGElement | null = $state(null);

	let currentSession = getCurrentSessionCtx();

	function updateSVGSize() {
		if (svg) {
			svg.setAttribute('width', svg.parentElement?.clientWidth.toString() || window.innerWidth.toString());
			svg.setAttribute('height', svg.parentElement?.clientHeight.toString() || window.innerHeight.toString());
		}
	}

	const realTimeActions = {
		create: (record: NodeMessage) => {
			if (!currentSession.admin.isAdmin && currentSession.ai && record?.type === 'event' && record.side) {
				const userSide = localStorage.getItem('side_' + currentSession.session.id);
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
				filter: `session="${currentSession.session.id}"`
			}
		);
	}

	onMount(async () => {
		if (!svg) return;

		updateSVGSize();
		graph = new MainGraph(svg, nodes, currentSession.sides, {
			width: Number(svg.getAttribute('width')) || window.innerWidth,
			height: Number(svg.getAttribute('height')) || window.innerHeight
		});

		// IA + not admin => filter the graph according to the chosen side
		// for special scenario
		if (currentSession.ai && !currentSession.admin && currentSession.sessionProfile.choosedSideId) {
			graph.filterNodeBySide(currentSession.sessionProfile.choosedSideId);
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
	onresize={() => {
		if (!svg) return;
		updateSVGSize();
		graph?.setOptions({
			width: Number(svg.getAttribute('width')) || window.innerWidth,
			height: Number(svg.getAttribute('height')) || window.innerHeight
		});
	}}
/>

<div class="h-full w-full">
	<svg
		bind:this={svg} 
		class="z-10 cursor-grab bg-dotted-40 bg-dotted-gray h-full w-full">
	</svg>
</div>
