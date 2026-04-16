export type AICapability = 'canCensor' | 'canTriggerNodes' | 'canEndSession';

export interface AINodeDef {
	title: string;
	text: string;
	author: string;
	side: string;
}

export interface AITriggerRule {
	condition: string;
	node: AINodeDef;
	requiresFired?: number[];
}

export interface AIConfig {
	vision: string;
	capabilities: AICapability[];
	script: {
		bannedWords?: string[];
		triggerRules?: AITriggerRule[];
		endCondition?: { condition: string; endTitle: string };
	};
}

export interface MistralAnalysisResponse {
	capabilities: AICapability[];
	explanation: string;
	fullySupported: boolean;
}
