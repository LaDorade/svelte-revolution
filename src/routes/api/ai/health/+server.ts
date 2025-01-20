import { apiHealthy } from '$lib/server/ia';
import { json } from '@sveltejs/kit';

export const POST = async () => {
	const aiHealthy = await apiHealthy();

	return json({ aiHealthy });
};
