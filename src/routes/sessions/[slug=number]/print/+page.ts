import type { GraphNode } from '$types/pocketBase/TableTypes';
import type { ServerLoad } from '@sveltejs/kit';

export const load: ServerLoad = async ({ parent }) => {
	const parentData = await parent();
	const nodes = (await parentData.nodesPromise) as GraphNode[];

	return {
		nodes
	};
};
