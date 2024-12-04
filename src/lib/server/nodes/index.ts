import sanitizeHtml from 'sanitize-html';
import type { MyPocketBase } from '$types/pocketBase';
import type { NodeType, Scenario } from '$types/pocketBase/TableTypes';

export async function createNode(
	pb: MyPocketBase,
	title: string,
	text: string,
	author: string,
	session: string,
	parent: string,
	sideId: string,
	type: NodeType = 'contribution'
) {
	title = sanitizeHtml(title);
	text = sanitizeHtml(text);
	author = sanitizeHtml(author);
	return await pb.collection('Node').create({
		title,
		text,
		author,
		session,
		type,
		side: sideId,
		parent
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
