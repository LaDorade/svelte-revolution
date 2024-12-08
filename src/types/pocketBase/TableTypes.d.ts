import type { BaseNode } from '$types/graph';

export type NodeType = 'contribution' | 'event' | 'startNode' | 'hidden'; // hidden is not in the database
export type Lang = 'fr' | 'en' | 'jp';
export type Role = 'admin' | 'user' | 'superAdmin'; // see in the database

export interface GraphNode extends BaseNode {
	author: string;
	session: string;
	type: NodeType;
	parent: string;
	side: string;
	sideNumber: number;
	expand?: {
		side?: Side;
	};
}

export interface Scenario {
	id: string;
	title: string;
	prologue: string;
	lang: Lang;
	ai?: boolean;
	firstNodeTitle: string;
	firstNodeText: string;
	firstNodeAuthor: string;
}

export interface End {
	id: string;
	title: string;
	text: string;
}

export interface GraphEvent {
	id: string;
	title: string;
	text: string;
	author: string;
}

export interface Session {
	id: string;
	slug: number;
	name: string;
	image: string;
	completed: boolean;
	visible: boolean;
	public: boolean;
	scenario: string;
	events: string[];
	author: string;
	end?: string;
	created: Date;
	expand?: {
		scenario?: Scenario;
		end?: End;
		events?: GraphEvent[];
		author?: User;
	};
}

export interface Side {
	id: string;
	name: string;
	number: number;
}

export interface User {
	id: string;
	username: string;
	role: Role;
	email?: string;
	name?: string;
	avatar?: string;
}
