<script lang="ts">
	//TODO: Refactor this component to use the new Graph class
	import { onDestroy, onMount, untrack } from 'svelte';
	import {
		zoom as d3Zoom,
		drag,
		forceLink,
		forceManyBody,
		forceRadial,
		forceSimulation,
		forceX,
		forceY,
		select,
		zoomIdentity,
		type Selection,
		type Simulation,
		type SimulationNodeDatum,
		type SimulationLinkDatum,
		type D3DragEvent
	} from 'd3';
	import { homeStore, type ExampleNode } from '$stores/graph/home/index.svelte';
	import { scale } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { t } from 'svelte-i18n';

	const width = 300;
	const forces = {
		forceX: 2,
		forceY: 2,
		forceLink: 1.2,
		distanceLink: 80,
		radialStrength: 0.3,
		charge: -600,
		radius: 50
	};

	const zoom = d3Zoom().on('zoom', (e) => {
		const { transform } = e;
		nodeLayer.attr('transform', transform);
		labelLayer.attr('transform', transform);
		const strokeWidth = 3 / Math.sqrt(transform.k);
		nodeLayer.style('stroke-width', strokeWidth);
		labelLayer.style('stroke-width', strokeWidth);
	});

	let svg: SVGElement;
	let svgElement: Selection<SVGElement, unknown, null, undefined>;
	let nodeLayer: Selection<SVGGElement, unknown, null, undefined>;
	let labelLayer: Selection<SVGGElement, unknown, null, undefined>;

	let link: { source: ExampleNode; target: ExampleNode }[];
	let node: ExampleNode[];
	let label: ExampleNode[];

	let simulation: Simulation<ExampleNode, SimulationLinkDatum<ExampleNode>> = forceSimulation(homeStore.nodes)
		.force(
			'link',
			forceLink<ExampleNode, SimulationLinkDatum<ExampleNode>>(homeStore.links)
				.id((d) => d.id)
				.distance(forces.distanceLink)
				.strength(forces.forceLink)
		)
		.force('charge', forceManyBody().strength(forces.charge))
		.force('centerNode', forceRadial(forces.radius, width / 2, width / 2).strength(forces.radialStrength))
		.force(
			'x',
			forceX<ExampleNode>(width).strength((d) => (d.id === homeStore.selectedNode?.id ? forces.forceX : 0))
		)
		.force(
			'y',
			forceY<ExampleNode>(width).strength((d) => (d.id === homeStore.selectedNode?.id ? forces.forceY : 0))
		);

	function dragstarted(event: D3DragEvent<SVGElement, SimulationNodeDatum, undefined>, d: SimulationNodeDatum) {
		if (!event.active) simulation.alphaTarget(0.3).restart();
		d.fx = d.x;
		d.fy = d.y;
	}
	function dragged(event: D3DragEvent<SVGElement, SimulationNodeDatum, undefined>, d: SimulationNodeDatum) {
		d.fx = event.x;
		d.fy = event.y;
	}
	function dragended(event: D3DragEvent<SVGElement, SimulationNodeDatum, undefined>, d: SimulationNodeDatum) {
		if (!event.active) simulation.alphaTarget(0);
		d.fx = null;
		d.fy = null;
	}

	$effect(() => {
		if (homeStore.selectedNode) {
			untrack(() => {
				simulation
					.force(
						'x',
						forceX<ExampleNode>(width / 2).strength((d) =>
							d.id === homeStore.selectedNode?.id ? forces.forceX : 0
						)
					)
					.force(
						'y',
						forceY<ExampleNode>(width / 2).strength((d) =>
							d.id === homeStore.selectedNode?.id ? forces.forceY : 0
						)
					);
				simulation.alpha(0.1).restart();
			});
		}
		if (homeStore.selectedNode?.id === 5) {
			//@ts-expect-error d3...
			svgElement?.call(zoom).call(zoom.transform, zoomIdentity);
		}
	});

	onMount(() => {
		svgElement = select(svg);
		nodeLayer = svgElement.append('g');
		labelLayer = svgElement.append('g');

		label = labelLayer
			.append('g')
			.selectAll('text')
			.data(homeStore.nodes)
			.enter()
			.append('text')
			.text((d) => $t(d.title))
			.attr('dy', () => -18)
			.attr('fill', 'white')
			.attr('font-size', 12)
			.attr('text-anchor', 'middle')
			.attr('alignment-baseline', 'middle')
			.style('cursor', 'pointer')
			// @ts-expect-error d3...
			.call(drag().on('start', dragstarted).on('drag', dragged).on('end', dragended))
			.on('click', (event, d) => {
				homeStore.selectedNode = d;
			});

		link = nodeLayer
			.append('g')
			.selectAll('line')
			.data(homeStore.links)
			.enter()
			.append('line')
			.attr('stroke', '#999')
			.attr('stroke-width', 2);

		node = nodeLayer
			.append('g')
			.selectAll('g')
			.data(homeStore.nodes)
			.enter()
			.append('g')
			.style('cursor', 'pointer')
			// @ts-expect-error d3...
			.call(drag().on('start', dragstarted).on('drag', dragged).on('end', dragended))
			.on('click', (event, d) => {
				homeStore.selectedNode = d;
			});

		node.append('path')
			.attr(
				'd',
				'M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z'
			)
			.attr('fill', 'white')
			.attr('stroke', 'black')
			.attr('stroke-width', 1);

		simulation.on('tick', () => {
			if (!node || !link || !label) return;
			// Mettre à jour la taille et la position de l'image
			node.select('path')
				.attr('transform', (d) => {
					if (d.id === homeStore.selectedNode?.id) {
						// La value de translate doit être adaptée à la scale que l'on met pour rester au centre
						return 'translate(-18,-18) scale(1.5)';
					} else {
						return 'translate(-12,-12) scale(1)';
					}
				})
				.attr('fill', (d) => (d.id === homeStore.selectedNode?.id ? 'black' : 'white'))
				.attr('stroke', (d) => (d.id === homeStore.selectedNode?.id ? 'white' : 'black'));

			// Déplacer le groupe entier (image + cercle) à la position du nœud
			node.attr('transform', (d) => `translate(${d.x},${d.y})`);

			// Mettre à jour les liens entre les nœuds
			link.attr('x1', (d) => d.source.x ?? 0)
				.attr('y1', (d) => Number(d.source.y) ?? 0)
				.attr('x2', (d) => Number(d.target.x) ?? 0)
				.attr('y2', (d) => Number(d.target.y) ?? 0);

			// Mettre à jour la position des labels
			label.attr('x', (d) => d.x).attr('y', (d) => d.y);
		});

		simulation.alpha(1).restart();
	});

	onDestroy(() => {
		simulation.stop();
	});
</script>

<div
	in:scale={{
		duration: 400,
		easing: quintOut,
		start: 0.2
	}}
	class="bg-black border-4 rounded-full w-fit bg-dotted-gray bg-dotted-20"
>
	<svg bind:this={svg} {width} height={width} class="rounded-full"> </svg>
</div>
