// TODO: change for the new Store system
import { linksStore, nodesStore, selectedNodeStore } from '$stores/graph';
import { get } from 'svelte/store';
import type { LinkMessage, NodeMessage } from '$types/graph';
import type { BaseType } from 'd3';
import * as d3 from 'd3';

export const colors = {
	startNode: '#1b3022',
	selectedNode: 'red',
	eventNode: '#f7b32b',
	defaultNode: '#86efac',
	defaultLink: '#999',
	hoverLink: 'red',
	connectedNode: 'purple'
};

export const strokeDashArray = {
	default: '5, 15',
	hover: 'none'
};

export const nodeRadius = {
	default: 10,
	selected: 15,
	start: 30,
	event: 20
};

function selectNode(node: NodeMessage) {
	if (get(selectedNodeStore)?.id === node.id) {
		selectedNodeStore.set(null);
		return;
	}
	selectedNodeStore.set(node);
}

export const updateLabelsInGraph = (
	labelLayer: d3.Selection<SVGGElement, NodeMessage, SVGElement, unknown>,
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	updatedNodes: d3.Selection<SVGGElement, NodeMessage, SVGElement, unknown>,
	simulation: d3.Simulation<NodeMessage, LinkMessage>
) => {
	const links = get(linksStore);
	const selectedNode = get(selectedNodeStore);
	return (
		labelLayer
			.selectAll('text')
			.data(get(nodesStore))
			.join('text')
			.attr('text-anchor', 'middle')
			.attr('dy', (d) => {
				return d.type !== 'startNode' ? -13 : 5;
			})
			.classed('fill-white', true)
			.style('font-size', '18px') // TODO personalize font size
			.text((d) => d.title)
			.on('click', (_, d) => selectNode(d))
			.style('cursor', 'pointer')
			// @ts-expect-error d3...
			.on('mouseover', (_, d) => handleMouseOver(d, linksInGraph, updatedNodes, links))
			// @ts-expect-error d3...
			.on('mouseout', () => handleMouseOut(linksInGraph, updatedNodes, selectedNode))
			.call(
				// @ts-expect-error d3....
				d3
					.drag<never, NodeMessage>()
					.on('start', (event, d) => handleDragStart(event, d, simulation))
					.on('drag', (event, d) => handleDrag(event, d))
					.on('end', (event, d) => handleDragEnd(event, d, simulation)),
				null
			)
	);
};

export const updateLinksInGraph = (linkLayer: d3.Selection<SVGGElement, NodeMessage, null, undefined>) => {
	return linkLayer
		.selectAll('line')
		.data(get(linksStore))
		.join('line')
		.attr('stroke', '#999')
		.attr('stroke-opacity', 1)
		.attr('stroke-width', 1)
		.attr('stroke-linecap', 'round')
		.attr('stroke-linejoin', 'round')
		.attr('stroke-dashoffset', 0)
		.attr('stroke-dasharray', strokeDashArray.default);
};

export const updateNodesInGraph = (
	nodeLayer: d3.Selection<SVGGElement, NodeMessage, SVGElement, unknown>,
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	simulation: d3.Simulation<NodeMessage, LinkMessage>
) => {
	const nodes = get(nodesStore);
	const selectedNode = get(selectedNodeStore);
	const links = get(linksStore);

	const updatedNodes = nodeLayer
		.selectAll('circle')
		.data(nodes)
		.join('circle')
		.attr('draggable', true)
		.attr('r', (d) => getNodeRadius(d, selectedNode))
		.style('cursor', 'pointer')
		.attr('fill', (d) => getNodeColor(d, selectedNode))
		.on('mouseover', (_, d) => handleMouseOver(d, linksInGraph, updatedNodes, links))
		.on('mouseout', () => handleMouseOut(linksInGraph, updatedNodes, selectedNode))
		.call(
			d3
				// @ts-expect-error d3...
				.drag<BaseType | SVGCircleElement, NodeMessage>()
				.on('start', (event, d) => handleDragStart(event, d, simulation))
				.on('drag', (event, d) => handleDrag(event, d))
				.on('end', (event, d) => handleDragEnd(event, d, simulation))
		)
		.on('click', (_, d) => selectNode(d));

	return updatedNodes;
};

const getNodeRadius = (d: NodeMessage, selectedNode: NodeMessage | null) => {
	if (d.type === 'startNode') {
		return nodeRadius.start;
	} else if (d.type === 'event') {
		return nodeRadius.event;
	} else if (selectedNode && selectedNode.id === d.id) {
		return nodeRadius.selected;
	} else {
		return nodeRadius.default;
	}
};

const getNodeColor = (d: NodeMessage, selectedNode: NodeMessage | null) => {
	if (selectedNode && selectedNode.id === d.id) {
		return colors.selectedNode;
	} else if (d.type === 'event') {
		return colors.eventNode;
	} else if (d.type === 'startNode') {
		return colors.startNode;
	}
	return colors.defaultNode;
};

const handleMouseOver = (
	d: NodeMessage,
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	updatedNodes: d3.Selection<BaseType | SVGCircleElement, NodeMessage, SVGElement, NodeMessage>,
	links: LinkMessage[]
) => {
	linksInGraph
		.attr('stroke-dasharray', (l) =>
			l.source === d || l.target === d ? strokeDashArray.hover : strokeDashArray.default
		)
		.attr('stroke', (l) => (l.source === d || l.target === d ? colors.hoverLink : colors.defaultLink))
		.attr('stroke-width', (l) => (l.source === d || l.target === d ? 2 : 1));

	updatedNodes.attr('fill', (n) => {
		if (n === d) return colors.selectedNode;
		if (links.some((l) => (l.source === d && l.target === n) || (l.target === d && l.source === n))) {
			return colors.connectedNode;
		} else if (n.type === 'startNode') {
			return colors.startNode;
		}
		return colors.defaultNode;
	});
};

const handleMouseOut = (
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	updatedNodes: d3.Selection<BaseType | SVGCircleElement, NodeMessage, SVGElement, unknown>,
	selectedNode: NodeMessage | null
) => {
	linksInGraph
		.attr('stroke-dasharray', strokeDashArray.default)
		.attr('stroke', colors.defaultLink)
		.attr('stroke-width', 1);
	updatedNodes.attr('fill', (d) => getNodeColor(d, selectedNode));
};

const handleDragStart = (
	event: d3.D3DragEvent<SVGElement, NodeMessage, NodeMessage>,
	d: NodeMessage,
	simulation: d3.Simulation<NodeMessage, undefined>
) => {
	if (!event.active) simulation.alphaTarget(0.3).restart();
	d.fx = d.x;
	d.fy = d.y;
};

const handleDrag = (event: d3.D3DragEvent<SVGElement, NodeMessage, NodeMessage>, d: NodeMessage) => {
	d.fx = event.x;
	d.fy = event.y;
};

const handleDragEnd = (
	event: d3.D3DragEvent<SVGElement, NodeMessage, NodeMessage>,
	d: NodeMessage,
	simulation: d3.Simulation<NodeMessage, undefined>
) => {
	if (!event.active) simulation.alphaTarget(0);
	d.fx = null;
	d.fy = null;
};
