import { DB_URL } from '$env/static/private';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { apiHealthy, getURL } from '$lib/server/ia';
import PocketBase from 'pocketbase';

export const POST: RequestHandler = async ({ request }) => {
	const url = getURL('associate');
	if (!(await apiHealthy()) || !url) {
		return json({ ok: false, message: 'IA server not reachable' });
	}

	const { sessionId, scenarioId, cookies } = await request.json();

	const pb = new PocketBase(DB_URL);
	pb.authStore.loadFromCookie(cookies);
	if (!pb.authStore.isValid) {
		return json({ ok: false, message: 'Invalid credentials' });
	}

	const sides = await pb
		.collection('side')
		.getFullList({ filter: pb.filter('scenario = {:scenario}', { scenario: scenarioId }) });
	const ends = await pb
		.collection('end')
		.getFullList({ filter: pb.filter('scenario = {:scenario}', { scenario: scenarioId }) });

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			session: sessionId,
			sides: sides.map((side) => {
				return { id: side.id, name: side.name };
			}),
			ends: ends.map((end) => {
				return { id: end.id, title: end.title };
			})
		})
	});
	return json(response.ok);
};
