import { availableLocales } from '../i18n';
import { z } from 'zod';
import { eventSchema } from './event.schema';

// test file : tests/units/scenario.test.ts
export const sideSchema = z.object({
	title: z.string().min(3).max(50),
	color: z
		.string()
		.regex(/^#[0-9A-F]{6}$/)
		.optional()
});

export const endSchema = z.object({
	title: z.string().min(3).max(50),
	text: z.string().min(3).max(500)
});

export const nodeSchema = z.object({
	title: z.string().min(3).max(50),
	text: z.string().min(3).max(500),
	author: z.string().min(1).max(50)
});

export const scenarioSchema = z.object({
	title: z.string().min(3).max(50),
	prologue: z.string().min(3).max(500),
	lang: z.enum([...availableLocales]),
	ai: z.boolean().optional()
});

export const fullScenarioSchema = z.object({
	...scenarioSchema.shape,
	firstNode: nodeSchema,
	sides: z.array(sideSchema).min(2),
	events: z.array(eventSchema).min(1),
	ends: z.array(endSchema).min(1)
});
