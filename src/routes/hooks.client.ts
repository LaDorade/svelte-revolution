import { init as initI18n } from 'svelte-i18n';
import type { ClientInit } from '@sveltejs/kit';

export const init: ClientInit = async () => {
	await initI18n({
		initialLocale: 'fr-FR',
		fallbackLocale: 'en-US',
	});
};