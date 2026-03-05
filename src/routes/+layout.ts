import '$lib/i18n';
import { init } from 'svelte-i18n';
import { pb } from '$lib/client/pocketbase';
import type { LayoutLoad } from './$types';

export const ssr = false;
export const prerender = false;

export const load: LayoutLoad = async () => {
	await init({
		initialLocale: 'fr-FR',
		fallbackLocale: 'en-US',
	});
	if (pb.authStore.isValid && pb.authStore.record) {
		return {
			user: pb.authStore.record,
			isAdmin: ['superAdmin', 'admin'].includes(pb.authStore.record.role),
			isSuperAdmin: pb.authStore.record.role === 'superAdmin'
		};
	}
	return {
		user: null
	};
};
