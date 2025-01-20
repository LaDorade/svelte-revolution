import * as values from '$lib/mainGraph/values';
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

	getNodeIcon = (node: PreviewNode) => {
		if (node.type === 'startNode' || node.type === 'event' || node.type === 'hidden') {
			return values.eventIcon;
		} else {
			return values.graphIcons[node.sideNumber];
		}
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
		/*if (this.selectedNode?.type === 'contribution' && d.id === this.selectedNode?.id) {
			return values.graphColors.nodes.selected;
		}*/
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
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	getNodeScale = (d: PreviewNode) => {
		const selected = this.selectedNode?.id === d.id;
		if (d.type === 'startNode') {
			if (selected) return values.nodeScale.start.selected;
			return values.nodeScale.start.default;
		} else if (d.type === 'event') {
			if (selected) return values.nodeScale.event.selected;
			return values.nodeScale.event.default;
		} else {
			if (selected) return values.nodeScale.default.selected;
			return values.nodeScale.default.default;
		}
	};
}
