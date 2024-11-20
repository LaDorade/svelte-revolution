import { env } from '$env/dynamic/private';

const iaServerUrl = env.IA_SERVER_URL;
const URLs = {
	health: '/api/health',
	checkMsg: '/api/checkMsg'
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

export async function censorNode<T extends { title: string; text: string }>(node: T): Promise<T> {
	const url = getURL('checkMsg');
	if (!url) return node;

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(node)
	});

	if (!response.ok) return node;

	const censored = await response.json();
	return censored;
}
