import { getLocaleFromNavigator, init, register, waitLocale } from 'svelte-i18n';

register('fr-FR', () => import('../lang/fr.json'));
register('en-US', () => import('../lang/en.json'));
register('es-ES', () => import('../lang/es.json'));
register('jp-JP', () => import('../lang/jp.json'));

export const availableLocales = ['fr', 'en', 'es', 'jp'] as const;

init({
	fallbackLocale: 'fr-FR',
	initialLocale: getLocaleFromNavigator()
});

waitLocale();
