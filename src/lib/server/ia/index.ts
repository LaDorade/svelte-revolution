import { env } from '$env/dynamic/private';
import type { AICensorResponse } from '$types/ai';

const iaServerUrl = env.IA_SERVER_URL;
const URLs = {
	health: '/api/health',
	checkMsg: '/api/checkMsg',
	associate: '/api/newSession'
};

export function getURL(url: keyof typeof URLs) {
	return iaServerUrl ? `${iaServerUrl}${URLs[url]}` : null;
}

export async function apiHealthy() {
	if (!iaServerUrl) {
		console.error('IA server URL not defined');
		return false;
	}
	const url = getURL('health');

	if (!url) return false;

	try {
		const response = await fetch(url);
		return response.ok;
	} catch (e) {
		const err = e as Error;
		console.error('IA server not reachable:', err.message);
		console.trace('IA server URL:', iaServerUrl);
		return false;
	}
}

export async function censorNode<T extends { title: string; text: string; session: string }>(
	node: T
): Promise<{
	node: T;
	triggerEvent: boolean;
	triggerEnd?: string;
	events: AICensorResponse['events'] | null;
}> {
	const url = getURL('checkMsg');
	const returnValue = { node, triggerEvent: false, events: null };
	if (!(await apiHealthy()) || !url) return returnValue;

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(node)
	});
	if (!response.ok) return returnValue;

	const data = (await response.json()) as AICensorResponse;

	const newNode = node;
	if (data.isCensored) {
		newNode.title = data.title;
		newNode.text = data.text;
	}
	return {
		node: newNode,
		triggerEvent: data.triggerNewEvent,
		events: data.events,
		triggerEnd: data.triggerEnd
	};
}
