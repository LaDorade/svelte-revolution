import { z } from 'zod';

// TODO: find a way to translate error messages
export const addNodeSchema = z.object({
	title: z.string({ message: 'errors.missingTitle' }).min(1),
	text: z.string({ message: 'errors.missingText' }).min(1),
	author: z.string({ message: 'errors.missingAuthor' }).min(1),
	parent: z.string({ message: 'errors.addNode.missingParent' }).min(1),
	session: z.string({ message: 'errors.addNode.missingSession' }).min(1),
	side: z.string({ message: 'errors.addNode.missingSide' }).min(1)
});
