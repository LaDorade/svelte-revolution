import type { User } from '$types/pocketBase/TableTypes';
import type { ServerLoad } from '@sveltejs/kit';

export const load: ServerLoad = async ({ locals }) => {
	const pb = locals.pb;
	if (pb.authStore.isValid && pb.authStore.model) {
		return {
			user: pb.authStore.model as User,
			isAdmin: ['superAdmin', 'admin'].includes(pb.authStore.model.role),
			isSuperAdmin: pb.authStore.model.role === 'superAdmin'
		};
	}
	return {
		user: null
	};
};
