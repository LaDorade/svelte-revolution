import { init as initI18n } from 'svelte-i18n';
import type { ServerInit } from '@sveltejs/kit';

export const init: ServerInit = async () => {
	await initI18n({
		initialLocale: 'fr-FR',
		fallbackLocale: 'en-US',
	});
};