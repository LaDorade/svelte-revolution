import { pb } from '$lib/client/pocketbase';

export const load = async () => {
	try {
		const sessions = await pb.collection('Session')
			.getFullList({ expand: 'scenario, author' });

		return { sessions };
	} catch (error) {
		console.error('Error fetching sessions:', error);
		return { sessions: [] };
	}
};
