export type AICensorResponse = {
	isCensored: boolean;
	title: string;
	text: string;
	triggerNewEvent: boolean;
	events?: {
		qg: {
			title: string;
			text: string;
			author: string;
		};
		terrain: {
			title: string;
			text: string;
			author: string;
		};
	};
};
