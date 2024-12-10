import { z } from 'zod';

export const createSessionSchema = z.object({
	name: z.string().min(3).max(50),
	scenarioId: z.string(),
	image: z.any().optional()
});
