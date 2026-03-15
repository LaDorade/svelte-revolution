import { pb } from '$lib/client/pocketbase';
import { redirect } from '@sveltejs/kit';

import type { Session } from '$types/pocketBase/TableTypes';
import type { LayoutLoad } from './$types';

export const ssr = false; // We don't need server-side rendering for admin pages
// plus, it causes weird loops with the pb.authStore

export const load: LayoutLoad = async ({ url }) => {
	if (!pb.authStore.isValid || !pb.authStore.record) {
		pb.authStore.clear();
		return redirect(303, '/login');
	}
	const user = pb.authStore.record;

	const sessions = await pb.collection('Session').getFullList({
		filter: pb.filter('author = {:user}', { user: user.id }),
		expand: 'scenario'
	});
	let otherSessions: Session[] = [];
	if (user.role === 'superAdmin') {
		otherSessions = await pb.collection('Session').getFullList({
			filter: pb.filter('author != {:user}', { user: user.id }),
			expand: 'scenario, author'
		});
	}

	return {
		sessions,
		otherSessions,
		user: user,
		route: url.pathname
	};
};
