import { z } from 'zod';

export const triggerSchema = z.object({
    triggerExpressions: z
        .string()
        .min(1)
        .max(100)
        .transform(val => val.split(',').map(expr => expr.trim()).filter(Boolean)),
    conditions: z
        .string()
        .regex(/^(\d+(,\d+)*)?$/, { message: "Conditions must be integer list separated by commas (eg: 1,2,3)" })
        .transform(val => val.split(',').filter(Boolean).map(Number)),
    title: z.string().min(3).max(50),
    text: z.string().min(3).max(500),
    author: z.string().min(1).max(50)
});
