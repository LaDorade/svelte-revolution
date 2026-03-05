import { z } from 'zod';

export const pseudoSchema = z.string().min(2).max(25);
