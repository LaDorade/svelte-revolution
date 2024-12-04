import { env } from '$env/dynamic/private';
import { createPocketBase } from '../pocketbase';

export const authIA = async () => {
	try {
		if (!env.IA_USERNAME || !env.IA_PASSWORD) return;
		const pb = createPocketBase();
		await pb.collection('Users').authWithPassword(env.IA_USERNAME, env.IA_PASSWORD);
		return pb;
	} catch (err) {
		console.error('Error:', err);
	}
};
