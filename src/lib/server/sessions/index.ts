import { error } from '@sveltejs/kit';
import { ClientResponseError } from 'pocketbase';
import type { Session } from '$types/pocketBase/TableTypes';
import { type MyPocketBase } from '../../../types/pocketBase/index';

export async function getSession(pb: MyPocketBase, sessionId: number) {
	let session: Session;
	try {
		session = await pb
			.collection('session')
			.getFirstListItem('slug=' + sessionId.toString(), { expand: 'end, scenario, events' });
	} catch (e) {
		const err = e as ClientResponseError;
		if (err.status === 404) {
			error(404, {
				status: 404,
				message: 'Session not found'
			});
		} else {
			error(500, {
				status: err.status,
				message: err.message
			});
		}
	}

	return session;
}

export async function createSession(
	pb: MyPocketBase,
	name: FormDataEntryValue,
	scenarioId: string,
	author: FormDataEntryValue,
	image: File
) {
	if (image.size !== 0) {
		image = new File([image as Blob], `${name}.png`, { type: 'image/png' });
	}
	const sessions = await pb.collection('Session').getFullList({ fields: 'id' });
	return await pb.collection('Session').create({
		name,
		scenario: scenarioId,
		author,
		slug: sessions.length + 1,
		public: true,
		visible: true,
		completed: false,
		image
	});
}
