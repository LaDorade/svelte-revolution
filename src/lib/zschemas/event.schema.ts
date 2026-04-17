import '$lib/i18n';
import { z } from 'zod';
import { _ } from 'svelte-i18n';
import { get } from 'svelte/store';

const t = get(_);


export const eventSchema = z.object({
	title: z
		.string()
		.min(3, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.event.event'),
					field: t('scenario.title'),
					x: 3
				}
			})
		})
		.max(50, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.event.event'),
					field: t('scenario.title'),
					x: 50
				}
			})
		}),
	text: z
		.string()
		.min(1, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.event.event'),
					field: t('scenario.text'),
					x: 1
				}
			})
		})
		.max(500, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.event.event'),
					field: t('scenario.text'),
					x: 500
				}
			})
		}),
	author: z
		.string()
		.min(1, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.event.event'),
					field: t('scenario.author'),
					x: 3
				}
			})
		})
		.max(50, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.event.event'),
					field: t('scenario.author'),
					x: 50
				}
			})
		})
});
