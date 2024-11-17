<script lang="ts">
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
	let svgElement: Selection<SVGSVGElement, unknown, null, undefined>;
	let nodeLayer: Selection<SVGGElement, ExampleNode, null, undefined>;
	let labelLayer: Selection<SVGGElement, ExampleNode, null, undefined>;

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
			forceX(width).strength((d) => (d.id === homeStore.selectedNode?.id ? forces.forceX : 0))
		)
		.force(
			'y',
			forceY(width).strength((d) => (d.id === homeStore.selectedNode?.id ? forces.forceY : 0))
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
						forceX(width / 2).strength((d) => (d.id === homeStore.selectedNode?.id ? forces.forceX : 0))
					)
					.force(
						'y',
						forceY(width / 2).strength((d) => (d.id === homeStore.selectedNode?.id ? forces.forceY : 0))
					);
				simulation.alpha(0.1).restart();
			});
		}
		if (homeStore.selectedNode?.id === 5) {
			svgElement?.call(zoom).call(zoom.transform, zoomIdentity);
		}
	});

	onMount(() => {
		untrack(() => {
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
				.selectAll('circle')
				.data(homeStore.nodes)
				.enter()
				.append('circle')
				.style('cursor', 'pointer')
				.call(drag().on('start', dragstarted).on('drag', dragged).on('end', dragended))
				.on('click', (event, d) => {
					homeStore.selectedNode = d;
				});

			simulation.on('tick', () => {
				if (!node || !link || !label) return;
				node.attr('cx', (d) => Number(d.x))
					.attr('cy', (d) => Number(d.y))
					.attr('r', (d) => (d.id === homeStore.selectedNode?.id ? 15 : 10))
					.attr('fill', (d) => (d.id === homeStore.selectedNode?.id ? 'yellow' : 'green'));

				link.attr('x1', (d) => d.source.x ?? 0)
					.attr('y1', (d) => Number(d.source.y) ?? 0)
					.attr('x2', (d) => Number(d.target.x) ?? 0)
					.attr('y2', (d) => Number(d.target.y) ?? 0);

				label.attr('x', (d) => d.x).attr('y', (d) => d.y);
			});

			simulation.alpha(1).restart();
		});
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
	<svg bind:this={svg} {width} height={width} class="rounded-full"></svg>
</div>
