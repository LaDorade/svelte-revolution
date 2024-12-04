import { env } from '$env/dynamic/private';
import type { AICensorResponse } from '$types/ai';

const iaServerUrl = env.IA_SERVER_URL;
const URLs = {
	health: '/api/health',
	checkMsg: '/api/checkMsg',
	associate: '/api/newSession'
};

function getURL(url: keyof typeof URLs) {
	return iaServerUrl ? `${iaServerUrl}${URLs[url]}` : null;
}

export async function apiHealthy() {
	if (!iaServerUrl) return false;
	const url = getURL('health');
	if (!url) return false;

	try {
		const response = await fetch(url);
		return response.ok;
	} catch {
		return false;
	}
}

export async function censorNode<T extends { title: string; text: string; session: string }>(
	node: T
): Promise<{ node: T; triggerEvent: boolean; events: AICensorResponse['events'] | null }> {
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
	if (data.isCensored) {
		node.title = data.title;
		node.text = data.text;
	}
	return { node: node, triggerEvent: data.triggerNewEvent, events: data.events };
}

export async function createAIAssociateSession(sessionId: string, bannedWords: string[]) {
	const url = getURL('associate');
	if (!(await apiHealthy()) || !url) return false;

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ session: sessionId, bannedWords })
	});

	return response.ok;
}
