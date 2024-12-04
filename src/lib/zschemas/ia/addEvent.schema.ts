import { z } from 'zod';
import { eventSchema } from '../event.schema';

export const addEventSchema = z.object({
	scenarioId: z.string(),
	sesssionId: z.string(),
	...eventSchema.shape
});
