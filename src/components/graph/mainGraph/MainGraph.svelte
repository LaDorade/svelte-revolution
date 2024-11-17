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
		zoomIdentity
	} from 'd3';
	import type { LinkMessage, NodeMessage } from '$types/graph';
	import { pb } from '$lib/client/pocketbase';
	// TODO: change for the new Store system
	import { linksStore, nodesStore, selectedNodeStore } from '$stores/graph';
	import { updateLabelsInGraph, updateLinksInGraph, updateNodesInGraph } from './utils';
	import toast from 'svelte-french-toast';
	import MessageToast from '$components/graph/MessageToast.svelte';
	import { type GraphNode } from '$types/pocketBase/TableTypes';
	import { buildLinks } from '$lib/sessions';

	interface Props {
		sessionId: string;
	}
	let { sessionId }: Props = $props();

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

		// simulation.force('center', forceCenter(currentWidth / 2, currentHeight / 2).strength(0.8))
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
		if (node) {
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
						if (typeof d.source !== 'object' || typeof d.target !== 'object') {
							return 100;
						}
						if (d.source.type === 'startNode' || d.target.type === 'startNode') {
							return 80;
						} else if (d.source.type === 'event' || d.target.type === 'event') {
							return 100;
						}
						return 100;
					})
					.strength(1)
			)
			.force('charge', forceManyBody().strength(-300));

		renderGraph();
	}

	onMount(async () => {
		// Real-time connection to the database
		await pb.collection('Node').subscribe(
			'*',
			async ({ action, record }) => {
				//action: 'create', 'update', 'delete'
				if (action === 'create') {
					const currentUser = localStorage.getItem('author');
					if (record.author !== currentUser) {
						// @ts-expect-error Svelte 5 problem I guess
						toast(MessageToast, {
							props: {
								author: record.author,
								record
							},
							duration: 4000,
							position: 'bottom-left',
							style: "{backgroundColor: 'rgba(0, 0, 0, 0.8)', color: 'white'}",
							icon: '📩'
						});
					}
					addNodeToGraph(record);
				} else if (action === 'update') {
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
				} else if (action === 'delete') {
					const newNodes = await pb.collection('Node').getFullList({ filter: `session="${sessionId}"` });
					nodesStore.set(newNodes);
					linksStore.set(buildLinks(newNodes));
					$selectedNodeStore = newNodes.find((node) => node.id === $selectedNodeStore?.parent) || null;
					restartSimulation();
				}
			},
			{
				filter: `session="${sessionId}"`
			}
		);

		initSimulation();
	});

	// Update the graph when a node is added
	const unsubscribe = selectedNodeStore.subscribe(() => {
		// hack to avoid the error "Cannot read property 'innerWidth' of undefined" on first render
		try {
			// eslint-disable-next-line
			window.innerWidth;
			renderGraph();
		} catch (error) {
			return error;
		}
	});

	onDestroy(() => {
		unsubscribe();
		simulation?.stop();
		pb.collection('Node').unsubscribe();
		selectedNodeStore.set(null);
		nodesStore.set([]);
		linksStore.set([]);
	});
</script>

<svelte:window on:resize={restartSimulation} />

<svg
	bind:this={svg}
	class="fixed top-0 left-0 w-screen h-screen z-10 cursor-grab bg-red-950 bg-opacity-40 bg-dotted-40 bg-dotted-gray
	[mask-image:radial-gradient(ellipse_80%_70%_at_50%_50%,#000_50%,transparent_100%)]"
>
</svg>
