import values from '$lib/mainGraph/values';
import Graph, { defaultGraphOptions, type GraphOptions } from './Graph.svelte';
import type { LinkMessage } from '$types/graph';
import type { PreviewNode, Side } from '$types/pocketBase/TableTypes';

export class PreviewGraph extends Graph<PreviewNode, LinkMessage> {
	sides: Side[] = [];
	constructor(
		svg: SVGElement,
		nodes: PreviewNode[],
		sides: Side[],
		options: Partial<GraphOptions> = defaultGraphOptions
	) {
		super(svg, nodes, options);
		this.sides = sides;
		this._nodes = nodes;
		$effect(() => {
			this.init();
		});
	}

	clearNodes = () => {
		this._nodes = [];
	};

	addNode = (node: PreviewNode) => {
		super.addNode(node);
		return true;
	};

	getNodeFill = (node: PreviewNode) => {
		if (node.type === 'startNode') {
			return values.graphColors.nodes.start;
		} else if (node.type === 'event') {
			return values.graphColors.nodes.event;
		} else if (this.selectedNode && this.selectedNode.id === node.id) {
			return values.graphColors.nodes.selected;
		} else if (node.type === 'hidden') {
			return values.graphColors.nodes.hidden;
		} else {
			return values.graphColors.nodes.sides[node.sideNumber];
		}
	};
	getLinkStroke = (l: LinkMessage) => {
		if (l.target.type === 'hidden') {
			return values.graphColors.links.toHide;
		}
		return values.graphColors.links.default;
	};
	getNodeStroke = (d: PreviewNode) => {
		if (this.selectedNode?.type === 'contribution' && d.id === this.selectedNode?.id) {
			return values.graphColors.nodes.sides[d.sideNumber];
		}
		return 'transparent';
	};
	getNodeRadius = (d: PreviewNode) => {
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
