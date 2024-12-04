<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import {
		forceLink,
		forceManyBody,
		forceRadial,
		forceSimulation,
		forceX,
		forceY,
		select,
		type Selection,
		type Simulation,
		type SimulationLinkDatum,
		zoom as d3Zoom,
		zoomIdentity,
		local
	} from 'd3';
	import { pb } from '$lib/client/pocketbase';
	import { watch } from '$lib/runes/watch.svelte';
	import { buildLinks } from '$lib/sessions';
	import { linksStore, nodesStore } from '$stores/graph';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';
	import type { LinkMessage, NodeMessage } from '$types/graph';
	import { type GraphNode, type Side } from '$types/pocketBase/TableTypes';
	import { updateLabelsInGraph, updateLinksInGraph, updateNodesInGraph } from './mainGraph';

	// Dev Feature to reinstanciate the component when the file is changed
	// ? It's because the hot reload is not working well with the d3 library
	if (import.meta.hot) {
		import.meta.hot.accept(() => {
			import.meta.hot?.invalidate();
		});
	}

	interface Props {
		sessionId: string;
		sides: Side[];
		iaConnected?: boolean;
	}
	let { sessionId, sides, iaConnected }: Props = $props();

	let svg: SVGElement;
	let svgElement: Selection<SVGElement, NodeMessage, null, undefined>;
	let nodeLayer: Selection<SVGGElement, NodeMessage, null, undefined>;
	let linkLayer: Selection<SVGGElement, NodeMessage, null, undefined>;
	let labelLayer: Selection<SVGGElement, NodeMessage, null, undefined>;

	let simulation: Simulation<NodeMessage, SimulationLinkDatum<NodeMessage>>;
	const zoom = d3Zoom().on('zoom', (e) => {
		const { transform } = e;
		nodeLayer.attr('transform', transform);
		linkLayer.attr('transform', transform);
		labelLayer.attr('transform', transform);
		const strokeWidth = 3 / Math.sqrt(transform.k);
		nodeLayer.style('stroke-width', strokeWidth);
		linkLayer.style('stroke-width', strokeWidth);
		labelLayer.style('stroke-width', strokeWidth);
	});

	function renderGraph() {
		if (!svgElement) {
			return;
		}
		const currentWidth = window?.innerWidth || 500;
		const currentHeight = window?.innerHeight || 500;
		svgElement.attr('width', currentWidth).attr('height', currentHeight);

		const linksInGraph = updateLinksInGraph(linkLayer);
		// @ts-expect-error d3...
		const nodesInGraph = updateNodesInGraph(nodeLayer, linksInGraph, simulation);
		// @ts-expect-error d3...
		const labelsInGraph = updateLabelsInGraph(labelLayer, linksInGraph, nodesInGraph, simulation);

		simulation.on('tick', () => {
			if (!linksInGraph || !nodesInGraph || !labelsInGraph) {
				return;
			}
			linksInGraph
				.attr('x1', (d) => String(d.source.x))
				.attr('y1', (d) => String(d.source.y))
				.attr('x2', (d) => String(d.target.x))
				.attr('y2', (d) => String(d.target.y));

			nodesInGraph.attr('cx', (d) => String(d.x)).attr('cy', (d) => String(d.y));
			labelsInGraph.attr('x', (d) => String(d.x)).attr('y', (d) => String(d.y));
		});

		simulation
			.force('centerNode', forceRadial(100, currentWidth / 2, currentHeight / 2).strength(0.02))
			.force(
				'x',
				forceX<GraphNode>(currentWidth / 2).strength((d) => (d.type === 'startNode' ? 1 : 0))
			)
			.force(
				'y',
				forceY<GraphNode>(currentHeight / 2).strength((d) => (d.type === 'startNode' ? 1 : 0))
			);
	}

	/**
	 * Append a new node and his links to the graph, then restart the simulation
	 */
	function addNodeToGraph(node: NodeMessage | null) {
		if (iaConnected && node?.type === 'event' && node.side) {
			const userSide = localStorage.getItem('side_' + sessionId);
			if (userSide !== node.side) {
				return;
			}
		}
		if (node) {
			// handle this in db
			node.sideNumber = sides.find((s: Side) => s.id === node.side)?.number ?? 0;
			nodesStore.set([...$nodesStore, node]);
		}
		linksStore.set(buildLinks($nodesStore));
		restartSimulation();
	}

	function restartSimulation() {
		simulation.nodes($nodesStore);
		// @ts-expect-error d3...
		simulation.force('link')?.links($linksStore);
		simulation.alpha(1).restart();
		renderGraph();
	}

	function initSimulation() {
		svgElement = select(svg);
		linkLayer = svgElement.append('g');
		nodeLayer = svgElement.append('g');
		labelLayer = svgElement.append('g');

		// @ts-expect-error d3...
		svgElement.call(zoom).call(zoom.transform, zoomIdentity);

		simulation = forceSimulation($nodesStore)
			.force(
				'link',
				forceLink<NodeMessage, LinkMessage>($linksStore)
					.id((d) => d.id)
					.distance((d) => {
						// if (typeof d.source !== 'object' || typeof d.target !== 'object') {
						// 	return 100;
						// }
						if (d.source.type === 'startNode' || d.target.type === 'startNode') {
							return 80;
						} else if (d.source.type === 'event' || d.target.type === 'event') {
							return 100;
						}
						return 100;
					})
					.strength(2)
			)
			.force('charge', forceManyBody().strength(-500));

		renderGraph();
	}

	const realTimeActions = {
		create: (record: NodeMessage) => {
			addNodeToGraph(record);
		},
		update: (record: NodeMessage) => {
			nodesStore.set(
				$nodesStore.map((node) => {
					if (node.id === record.id) {
						node.text = record.text;
						node.title = record.title;
					}
					return node;
				})
			);
			renderGraph();
		},
		delete: async () => {
			const newNodes = await pb.collection('Node').getFullList({ filter: `session="${sessionId}"` });
			nodesStore.set(newNodes);
			linksStore.set(buildLinks(newNodes));
			mainGraphStore.selectedNode =
				newNodes.find((node) => node.id === mainGraphStore.selectedNode?.parent) || null;
			restartSimulation();
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
		await realTimeNodeUpdate();
		initSimulation();
	});

	$effect(() => {
		watch(() => {
			renderGraph();
		}, [mainGraphStore.selectedNode]);
	});

	onDestroy(() => {
		simulation?.stop();
		pb.collection('Node').unsubscribe();
		mainGraphStore.selectedNode = null;
		nodesStore.set([]);
		linksStore.set([]);
	});
</script>

<svelte:window on:resize={restartSimulation} />

<svg
	bind:this={svg}
	class="mainGraph fixed top-0 left-0 w-screen h-screen z-10 cursor-grab bg-opacity-40 bg-dotted-40 bg-dotted-gray
	[mask-image:radial-gradient(ellipse_80%_70%_at_50%_50%,#000_50%,transparent_100%)]"
>
</svg>
