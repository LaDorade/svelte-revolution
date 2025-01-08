import values from '$lib/mainGraph/values';
import Graph, { defaultGraphOptions, type GraphOptions } from './Graph.svelte';
import { t } from 'svelte-i18n';
import { get } from 'svelte/store';
import type { LinkMessage } from '$types/graph';
import type { GraphNode, Side } from '$types/pocketBase/TableTypes';

export class MainGraph extends Graph<GraphNode, LinkMessage> {
	sides: Side[] = [];
	constructor(
		svg: SVGElement,
		nodes: GraphNode[],
		sides: Side[],
		options: Partial<GraphOptions> = defaultGraphOptions
	) {
		super(svg, nodes, options);
		this.sides = sides;
		nodes = this.mapNodeSides(nodes);
		this._nodes = nodes;
		$effect(() => {
			this.init();
		});
	}

	mapNodeSides = (nodes: GraphNode[]) => {
		return nodes.map((n) => {
			return {
				...n,
				sideNumber: this.sides.find((s: Side) => s.id === n.side)?.number ?? 0
			};
		});
	};

	addNode = (node: GraphNode) => {
		const selectedNode = this.selectedNode;
		if (!selectedNode) {
			return false;
		}
		node.sideNumber = this.sides.find((s: Side) => s.id === node.side)?.number ?? 0;
		super.addNode(node);
		return true;
	};
	updateNode(node: GraphNode): void {
		node.sideNumber = this.sides.find((s: Side) => s.id === node.side)?.number ?? 0;
		super.updateNode(node);
	}

	filterNodeBySide(userSideId: number | string | null) {
		// Hide events from other side if it's an AI scenario
		const filteredText = get(t)('inSession.eventHidden');
		this._nodes = this._nodes.map((node) => {
			if (node.type === 'event' && node.side && node.side !== userSideId) {
				node.text = filteredText;
				node.title = filteredText;
				node.author = filteredText;
				node.type = 'hidden';
			}
			return node;
		});
	}

	getNodeIcon = (node: GraphNode) => {
		if (node.type === 'startNode' || node.type === 'event' || node.type === 'hidden') {
			return '';
		} else {
			return values.graphIcons[node.sideNumber];
		}
	};
	getNodeFill = (node: GraphNode) => {
		if (node.type === 'startNode') {
			return values.graphColors.nodes.start;
		} else if (node.type === 'event') {
			return values.graphColors.nodes.event;
		} else if (this.selectedNode && this.selectedNode.id === node.id) {
			return values.graphColors.nodes.selected;
		} else if (node.type === 'hidden') {
			return values.graphColors.nodes.hidden;
		} else {
			return values.graphColors.nodes.sides; //[node.sideNumber];
		}
	};
	getLinkStroke = (l: LinkMessage) => {
		if (l.target.type === 'hidden') {
			return values.graphColors.links.toHide;
		}
		return values.graphColors.links.default;
	};
	getNodeStroke = (d: GraphNode) => {
		if (this.selectedNode?.type === 'contribution' && d.id === this.selectedNode?.id) {
			return values.graphColors.nodes.sides[d.sideNumber];
		}
		return 'transparent';
	};
	getNodeRadius = (d: GraphNode) => {
		if (d.type === 'startNode') {
			return values.nodeRadius.start;
		} else if (d.type === 'event') {
			return values.nodeRadius.event;
		} else if (this.selectedNode && this.selectedNode.id === d.id) {
			return values.nodeRadius.selected;
		} else {
			return values.nodeRadius.default;
		}
	};
}
