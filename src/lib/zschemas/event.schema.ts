import { z } from 'zod';

export const eventSchema = z.object({
	title: z.string().min(3).max(50),
	text: z.string().min(3).max(500),
	author: z.string().min(1).max(50)
});
