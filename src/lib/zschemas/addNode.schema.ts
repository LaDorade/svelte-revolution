import { get } from 'svelte/store';
import { t } from 'svelte-i18n';
import { z } from 'zod';

export const addNodeSchema = z.object({
	title: z.string({ message: 'errors.missingTitle' }),
	text: z.string({ message: 'errors.missingText' }),
	author: z.string({ message: 'errors.missingAuthor' }),
	parent: z.string({ message: 'errors.addNode.missingParent' }),
	session: z.string({ message: 'errors.addNode.missingSession' }),
	side: z.string({ message: 'errors.addNode.missingSide' })
});
