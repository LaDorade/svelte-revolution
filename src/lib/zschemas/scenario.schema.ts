import '$lib/i18n';
import { availableLocales } from '$lib/i18n';
import { z } from 'zod';
import { eventSchema } from './event.schema';

import { _ } from 'svelte-i18n';
import { get } from 'svelte/store';

const t = get(_);

// TODO: translate error messages
// test file : tests/units/scenario.test.ts
export const sideSchema = z.object({
	title: z
		.string()
		.min(3, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('side.side'),
					field: t('scenario.title'),
					x: 3
				}
			})
		})
		.max(50, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('side.side'),
					field: t('scenario.title'),
					x: 50
				}
			})
		}),
});

export const endSchema = z.object({
	title: z
		.string()
		.min(3, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.end.end'),
					field: t('scenario.title'),
					x: 3
				}
			})
		})
		.max(50, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.end.end'),
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
					type: t('scenario.end.end'),
					field: t('scenario.text'),
					x: 1
				}
			})
		})
		.max(500, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.end.end'),
					field: t('scenario.text'),
					x: 500
				}
			})
		}),
});

export const nodeSchema = z.object({
	title: z
		.string()
		.min(3, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.node.node'),
					field: t('scenario.title'),
					x: 3
				}
			})
		})
		.max(50, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.node.node'),
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
					type: t('scenario.node.node'),
					field: t('scenario.text'),
					x: 1
				}
			})
		})
		.max(500, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.node.node'),
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
					type: t('scenario.node.node'),
					field: t('scenario.author'),
					x: 3
				}
			})
		})
		.max(50, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.node.node'),
					field: t('scenario.author'),
					x: 50
				}
			})
		})
});

export const scenarioSchema = z.object({
	title: z
		.string()
		.min(3, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.scenario'),
					field: t('scenario.title'),
					x: 3
				}
			})
		})
		.max(50, { message: 'Scenario title must be at most 50 characters long' }),
	prologue: z
		.string()
		.min(3, {
			message: t('errors.validation.fieldOftypeMustBeMinimumXLong', {
				values: {
					type: t('scenario.prologue'),
					field: t('scenario.title'),
					x: 3
				}
			})
		})
		.max(5000, {
			message: t('errors.validation.fieldOftypeMustBeMaximumXLong', {
				values: {
					type: t('scenario.prologue'),
					field: t('scenario.title'),
					x: 5000
				}
			})
		}),
	lang: z.enum([...availableLocales], { message: 'Invalid scenario language' }),
	ai: z.boolean().optional()
});

export const fullScenarioSchema = z.object({
	...scenarioSchema.shape,
	firstNode: nodeSchema,
	sides: z.array(sideSchema).min(2, { 
		message: t('errors.validation.thereMustBeAtLeastXItem',{
			values: {
				type: t('side.side'),
				x: 2
			}				
		})
	}),
	events: z.array(eventSchema).min(1, {
		message: t('errors.validation.thereMustBeAtLeastXItem',{
			values: {
				type: t('scenario.event.event'),
				x: 1
			}				
		})
	}),
	ends: z.array(endSchema).min(1, { 
		message: t('errors.validation.thereMustBeAtLeastXItem',{
			values: {
				type: t('scenario.end.end'),
				x: 1
			}				
		})
	})
});
