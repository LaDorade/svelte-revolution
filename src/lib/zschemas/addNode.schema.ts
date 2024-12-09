import { get } from 'svelte/store';
import { t } from 'svelte-i18n';
import { z } from 'zod';

export const addNodeSchema = z.object({
	title: z.string({ message: get(t)('errors.missingTitle') }),
	text: z.string({ message: get(t)('errors.missingText') }),
	author: z.string({ message: get(t)('errors.missingAuthor') }),
	parent: z.string({ message: get(t)('errors.addNode.missingParent') }),
	session: z.string({ message: get(t)('errors.addNode.missingSession') }),
	side: z.string({ message: get(t)('errors.addNode.missingSide') })
});
