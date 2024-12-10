import { linksStore, nodesStore } from '$stores/graph';
import type { LinkMessage, NodeMessage } from '$types/graph';
import type { GraphNode, Side } from '$types/pocketBase/TableTypes';

export function initStores(nodes: NodeMessage[] = [], links: LinkMessage[] = []) {
	nodesStore.set(nodes);
	linksStore.set(links);
}

export function mapNodeSides(nodes: GraphNode[], sides: Side[]): GraphNode[] {
	return nodes.map((n) => {
		return {
			...n,
			sideNumber: sides.find((s: Side) => s.id === n.side)?.number ?? 0
		};
	});
}
