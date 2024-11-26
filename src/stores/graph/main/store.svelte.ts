import type { NodeMessage } from '$types/graph';

function createMainGraphStore() {
	let selectedNode: NodeMessage | null = $state(null);

	return {
		get selectedNode() {
			return selectedNode;
		},
		set selectedNode(node: NodeMessage | null) {
			selectedNode = node;
		}
	};
}

export const mainGraphStore = createMainGraphStore();
