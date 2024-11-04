import { dev } from '$app/environment';
import { createPocketBase } from '$lib/server/pocketbase';
import { redirect, type Handle } from '@sveltejs/kit';

export const corsHeaders = {
	'Access-Control-Allow-Credentials': 'true',
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,PATCH,DELETE',
	'Access-Control-Allow-Headers':
		'authorization, x-client-info, apikey, X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
};
export const handle: Handle = async ({ event, resolve }) => {
	if (event.request.method === 'OPTIONS') {
		return new Response(null, {
			headers: corsHeaders
		});
	}

	if (event.request.url.endsWith('__data.json')) {
		redirect(300, event.request.url.replace(/__data.json$/, ''));
	}

	event.locals.pb = createPocketBase();
	event.locals.pb.authStore.loadFromCookie(event.request.headers.get('cookie') || '');

	if (event.locals.pb.authStore.isValid) {
		try {
			await event.locals.pb.collection('users').authRefresh();
		} catch {
			event.locals.pb.authStore.clear();
		}
	}

	const response = await resolve(event);

	response.headers.append(
		'set-cookie',
		event.locals.pb.authStore.exportToCookie({ httpOnly: false, path: '/', secure: dev ? false : false })
	);
	// httpOnly: if true, the cookie is not accessible via JavaScript, that's why we're setting it to false
	// path: '/' is the default, but we're setting it explicitly here
	// secure: if true, send cookie over HTTPS only

	return response;
};
