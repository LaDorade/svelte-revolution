import sanitizeHtml from 'sanitize-html';
import type { MyPocketBase } from '$types/pocketBase';
import type { GraphNode, Scenario } from '$types/pocketBase/TableTypes';

type CreateNode = Pick<GraphNode,
	'title' | 'text' | 'author' |
	'session' | 'type' | 'parent' | 'side'
	| 'audio'
>

export async function createNode(
	pb: MyPocketBase,
	insert: CreateNode
) {
	const title = sanitizeHtml(insert.title);
	const text = sanitizeHtml(insert.text);
	const author = sanitizeHtml(insert.author);

	return await pb.collection('Node').create({
		title,
		text,
		author,
		session: insert.session,
		type: insert.type,
		side: insert.side,
		parent: insert.parent,
		audio: insert.audio
	});
}


export async function createStartNode(pb: MyPocketBase, scenario: Scenario, sessionId: string) {
	return await pb.collection('Node').create({
		title: scenario.firstNodeTitle,
		text: scenario.firstNodeText,
		author: scenario.firstNodeAuthor,
		session: sessionId,
		type: 'startNode'
	});
}
