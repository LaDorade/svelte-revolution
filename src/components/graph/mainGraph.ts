import values from '$lib/mainGraph/values';
import * as d3 from 'd3';
import type { LinkMessage, NodeMessage } from '$types/graph';
import { get } from 'svelte/store';
import { mainGraphStore } from '$stores/graph/main/store.svelte';
// TODO: change for the new Store system
import { linksStore, nodesStore } from '$stores/graph';
import type { BaseType } from 'd3';

function selectNode(node: NodeMessage) {
	if (mainGraphStore.selectedNode?.id === node.id) {
		mainGraphStore.selectedNode = null;
		return;
	}
	mainGraphStore.selectedNode = node;
}

function getNodeFill(node: NodeMessage) {
	const selectedNode = mainGraphStore.selectedNode;
	if (node.type === 'startNode') {
		return values.graphColors.nodes.start;
	} else if (node.type === 'event') {
		return values.graphColors.nodes.event;
	} else if (selectedNode && selectedNode.id === node.id) {
		return values.graphColors.nodes.selected;
	} else if (node.type === 'hidden') {
		return values.graphColors.nodes.hidden;
	} else {
		return values.graphColors.nodes.sides[node.sideNumber];
	}
}

function getNodeRadius(d: NodeMessage, selectedNode: NodeMessage | null) {
	if (d.type === 'startNode') {
		return values.nodeRadius.start;
	} else if (d.type === 'event') {
		return values.nodeRadius.event;
	} else if (selectedNode && selectedNode.id === d.id) {
		return values.nodeRadius.selected;
	} else {
		return values.nodeRadius.default;
	}
}

function getLinkStroke(l: LinkMessage) {
	if (l.target.type === 'hidden') {
		return values.graphColors.links.toHide;
	}
	return values.graphColors.links.default;
}

export const updateLabelsInGraph = (
	labelLayer: d3.Selection<SVGGElement, NodeMessage, SVGElement, unknown>,
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	updatedNodes: d3.Selection<SVGGElement, NodeMessage, SVGElement, unknown>,
	simulation: d3.Simulation<NodeMessage, LinkMessage>
) => {
	const links = get(linksStore);
	const selectedNode = mainGraphStore.selectedNode;
	return (
		labelLayer
			.selectAll('text')
			.data(get(nodesStore))
			.join('text')
			.attr('text-anchor', 'middle')
			.attr('dy', (d) => {
				return -getNodeRadius(d, selectedNode) - 5;
			})
			.style('fill', (n) => {
				if (n.type === 'hidden') {
					return values.labels.hidden;
				}
				return values.labels.default;
			})
			.style('font-size', (d) => {
				return getNodeRadius(d, selectedNode) + 'px';
			}) // TODO personalize font size
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
		.attr('stroke', (d) => {
			return getLinkStroke(d);
		})
		.attr('stroke-opacity', 1)
		.attr('stroke-width', 1)
		.attr('stroke-linecap', 'round')
		.attr('stroke-linejoin', 'round')
		.attr('stroke-dashoffset', 0)
		.attr('stroke-dasharray', values.strokeDashArray.default);
};

export const updateNodesInGraph = (
	nodeLayer: d3.Selection<SVGGElement, NodeMessage, SVGElement, unknown>,
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	simulation: d3.Simulation<NodeMessage, LinkMessage>
) => {
	const nodes = get(nodesStore);
	const selectedNode = mainGraphStore.selectedNode;
	const links = get(linksStore);

	const updatedNodes = nodeLayer
		.selectAll('circle')
		.data(nodes)
		.join('circle')
		.attr('draggable', true)
		.attr('r', (d) => getNodeRadius(d, selectedNode))
		.style('cursor', 'pointer')
		.style('fill', (d) => {
			return getNodeFill(d);
		})
		.attr('stroke', (d) => {
			if (d.id === selectedNode?.id) {
				return values.graphColors.nodes.sides[d.sideNumber];
			}
			return null;
		})
		.attr('stroke-width', 4)
		// end colors
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

const handleMouseOver = (
	d: NodeMessage,
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	updatedNodes: d3.Selection<BaseType | SVGCircleElement, NodeMessage, SVGElement, NodeMessage>,
	links: LinkMessage[]
) => {
	linksInGraph
		.attr('stroke', (l) => {
			if (l.source === d || l.target === d) {
				return values.graphColors.links.hover;
			}
			return getLinkStroke(l);
		})
		.attr('stroke-dasharray', (l) =>
			l.source === d || l.target === d ? values.strokeDashArray.hover : values.strokeDashArray.default
		)
		.attr('stroke-width', (l) => (l.source === d || l.target === d ? 2 : 1));

	updatedNodes.style('fill', (n) => {
		if (n === d) {
			return values.graphColors.nodes.selected;
		} else if (links.some((l) => (l.source === d && l.target === n) || (l.target === d && l.source === n))) {
			return values.graphColors.nodes.connected;
		} else {
			return getNodeFill(n);
		}
	});
};

const handleMouseOut = (
	linksInGraph: d3.Selection<SVGGElement, LinkMessage, SVGElement, unknown>,
	updatedNodes: d3.Selection<BaseType | SVGCircleElement, NodeMessage, SVGElement, unknown>,
	selectedNode: NodeMessage | null
) => {
	linksInGraph
		.attr('stroke', (l) => {
			return getLinkStroke(l);
		})
		.attr('stroke-dasharray', values.strokeDashArray.default)
		.attr('stroke-width', 1);

	updatedNodes.style('fill', (n) => {
		if (n === selectedNode) {
			return values.graphColors.nodes.selected;
		} else {
			return getNodeFill(n);
		}
	});
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
