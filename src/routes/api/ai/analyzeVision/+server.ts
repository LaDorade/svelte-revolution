import { MISTRAL_API_KEY } from '$env/static/private';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import type { MistralAnalysisResponse } from '$types/ai';
import { aiCapabilities } from '$lib/zschemas/aiConfig.schema';

const MAX_VISION_BYTES = 8_000;

const SYSTEM_PROMPT = `You are an assistant that helps configure an AI Game Master for a collaborative storytelling platform called "Babel Révolution".
Analyze the scenario creator's vision and determine which of these three capabilities are relevant:
- canCensor: The AI can redact or block player-submitted story nodes based on content rules (e.g. banned words, forbidden topics).
- canTriggerNodes: The AI can automatically publish pre-written story nodes in response to specific player actions or conditions.
- canEndSession: The AI can trigger a story ending when a specific condition is met.

You MUST respond ONLY with a valid JSON object matching this exact structure, with no text outside it:
{
  "capabilities": ["canCensor", "canTriggerNodes"],
  "explanation": "Brief explanation of what the AI will do and why these capabilities match the vision",
  "fullySupported": true
}
Set "fullySupported" to false if the vision describes something that cannot be implemented with the three capabilities above.`;

export const POST: RequestHandler = async ({ request }) => {
	const contentLength = request.headers.get('content-length');
	if (contentLength && parseInt(contentLength) > MAX_VISION_BYTES) {
		return json({ error: 'Payload too large' }, { status: 413 });
	}

	const { vision, lang } = await request.json();

	if (!vision || typeof vision !== 'string' || vision.trim().length < 10) {
		return json({ error: 'Vision text is too short' }, { status: 400 });
	}

	const controller = new AbortController();
	const timeout = setTimeout(() => controller.abort(), 30_000);

	try {
		const response = await fetch('https://api.mistral.ai/v1/chat/completions', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${MISTRAL_API_KEY}`
			},
			body: JSON.stringify({
				model: 'mistral-small-latest',
				messages: [
					{ role: 'system', content: SYSTEM_PROMPT },
					{
						role: 'user',
						content: `Scenario language: ${lang}\nCreator's vision: ${vision}`
					}
				],
				temperature: 0.2,
				response_format: { type: 'json_object' }
			}),
			signal: controller.signal
		});

		if (!response.ok) {
			console.error('Mistral API error:', response.status, await response.text());
			return json({ error: 'AI analysis failed' }, { status: 502 });
		}

		const data = await response.json();
		const content = data.choices?.[0]?.message?.content;

		if (!content) {
			return json({ error: 'Empty response from AI' }, { status: 502 });
		}

		const parsed = JSON.parse(content) as MistralAnalysisResponse;

		parsed.capabilities = (parsed.capabilities ?? []).filter((c) => aiCapabilities.includes(c));

		return json(parsed);
	} catch (e) {
		console.error('analyzeVision error:', e);
		return json({ error: 'AI analysis failed' }, { status: 500 });
	} finally {
		clearTimeout(timeout);
	}
};
