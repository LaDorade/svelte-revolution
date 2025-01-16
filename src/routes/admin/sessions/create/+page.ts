import { pb } from '$lib/client/pocketbase';

export const load = async () => {
	const scenarios = await pb.collection('Scenario').getFullList();
	return {
		scenarios
	};
};
