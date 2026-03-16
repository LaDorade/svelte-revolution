import { availableLocales } from '../i18n';
import { z } from 'zod';
import { eventSchema } from './event.schema';

// TODO: translate error messages
// test file : tests/units/scenario.test.ts
export const sideSchema = z.object({
	title: z
		.string()
		.min(1, { message: 'Side title must be at least 1 character long' })
		.max(50, { message: 'Side title must be at most 50 characters long' })
});

export const endSchema = z.object({
	title: z
		.string()
		.min(3, { message: 'End title must be at least 3 characters long' })
		.max(50, { message: 'End title must be at most 50 characters long' }),
	text: z
		.string()
		.min(3, { message: 'End text must be at least 3 characters long' })
		.max(500, { message: 'End text must be at most 500 characters long' })
});

export const nodeSchema = z.object({
	title: z
		.string()
		.min(3, { message: 'Node title must be at least 3 characters long' })
		.max(50, { message: 'Node title must be at most 50 characters long' }),
	text: z
		.string()
		.min(3, { message: 'Node text must be at least 3 characters long' })
		.max(500, { message: 'Node text must be at most 500 characters long' }),
	author: z
		.string()
		.min(1, { message: 'Node author must be at least 1 character long' })
		.max(50, { message: 'Node author must be at most 50 characters long' })
});

export const scenarioSchema = z.object({
	title: z
		.string()
		.min(3, { message: 'Scenario title must be at least 3 characters long' })
		.max(50, { message: 'Scenario title must be at most 50 characters long' }),
	prologue: z
		.string()
		.min(3, { message: 'Scenario prologue must be at least 3 characters long' })
		.max(5000, { message: 'Scenario prologue must be at most 5000 characters long' }),
	lang: z.enum([...availableLocales], { message: 'Invalid scenario language' }),
	ai: z.boolean().optional()
});

export const fullScenarioSchema = z.object({
	...scenarioSchema.shape,
	firstNode: nodeSchema,
	sides: z.array(sideSchema).min(2, { message: 'There must be at least 2 sides in the scenario' }),
	events: z.array(eventSchema).min(1, { message: 'There must be at least 1 event in the scenario' }),
	ends: z.array(endSchema).min(1, { message: 'There must be at least 1 end in the scenario' })
});
