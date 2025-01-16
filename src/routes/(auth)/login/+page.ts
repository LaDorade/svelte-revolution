import { pb } from '$lib/client/pocketbase';
import { redirect } from '@sveltejs/kit';

export const load = async () => {
	if (pb.authStore.isValid) {
		return redirect(303, '/admin');
	}
	return {};
};
