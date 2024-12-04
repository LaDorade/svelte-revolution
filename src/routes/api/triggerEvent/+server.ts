import { authIA } from '$lib/server/ia/auth';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
	authIA({ username: 'username', password: 'password' });
	const data = await request.json();

	return new Response(JSON.stringify({ message: 'success' }), { status: 200 });
};
