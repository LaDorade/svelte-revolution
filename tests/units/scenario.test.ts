import { describe, expect, it } from 'vitest';
import { fullScenarioSchema } from '../../src/lib/zschemas/scenario.schema';

describe('Scenario Creation', () => {
	it('should validate a correct scenario', () => {
		const validScenario = {
			title: 'A valid title',
			prologue: 'A valid prologue',
			lang: 'en',
			sides: [{ title: 'Side 1' }, { title: 'Side 2' }],
			firstNode: {
				title: 'First Node Title',
				text: 'First Node Text',
				author: 'Author Name'
			},
			events: [{ title: 'Event 1', text: 'Event 1 Text', author: 'Author Name' }],
			ends: [{ title: 'End 1', text: 'End 1 Text' }]
		};

		expect(() => fullScenarioSchema.parse(validScenario)).not.toThrow();
	});

	it('should fail if title is too short', () => {
		const invalidScenario = {
			title: 'A',
			prologue: 'A valid prologue',
			lang: 'en-US',
			sides: [{ title: 'Side 1' }, { title: 'Side 2' }],
			firstNode: {
				title: 'First Node Title',
				text: 'First Node Text',
				author: 'Author Name'
			},
			events: [{ title: 'Event 1', text: 'Event 1 Text', author: 'Author Name' }],
			ends: [{ title: 'End 1', text: 'End 1 Text' }]
		};

		expect(() => fullScenarioSchema.parse(invalidScenario)).toThrow();
	});

	it('should fail if sides are less than 2', () => {
		const invalidScenario = {
			title: 'A valid title',
			prologue: 'A valid prologue',
			lang: 'en-US',
			sides: [{ title: 'Side 1' }],
			firstNode: {
				title: 'First Node Title',
				text: 'First Node Text',
				author: 'Author Name'
			},
			events: [{ title: 'Event 1', text: 'Event 1 Text', author: 'Author Name' }],
			ends: [{ title: 'End 1', text: 'End 1 Text' }]
		};

		expect(() => fullScenarioSchema.parse(invalidScenario)).toThrow();
	});

	it('should fail if lang is not in the enum', () => {
		const invalidScenario = {
			title: 'A valid title',
			prologue: 'A valid prologue',
			lang: 'de-DE',
			sides: [{ title: 'Side 1' }, { title: 'Side 2' }],
			firstNode: {
				title: 'First Node Title',
				text: 'First Node Text',
				author: 'Author Name'
			},
			events: [{ title: 'Event 1', text: 'Event 1 Text', author: 'Author Name' }],
			ends: [{ title: 'End 1', text: 'End 1 Text' }]
		};

		expect(() => fullScenarioSchema.parse(invalidScenario)).toThrow();
	});

	it('should fail if firstNode is missing', () => {
		const invalidScenario = {
			title: 'A valid title',
			prologue: 'A valid prologue',
			lang: 'en-US',
			sides: [{ title: 'Side 1' }, { title: 'Side 2' }],
			events: [{ title: 'Event 1', text: 'Event 1 Text', author: 'Author Name' }],
			ends: [{ title: 'End 1', text: 'End 1 Text' }]
		};

		expect(() => fullScenarioSchema.parse(invalidScenario)).toThrow();
	});

	it('should fail if events are less than 1', () => {
		const invalidScenario = {
			title: 'A valid title',
			prologue: 'A valid prologue',
			lang: 'en-US',
			sides: [{ title: 'Side 1' }, { title: 'Side 2' }],
			firstNode: {
				title: 'First Node Title',
				text: 'First Node Text',
				author: 'Author Name'
			},
			events: [],
			ends: [{ title: 'End 1', text: 'End 1 Text' }]
		};

		expect(() => fullScenarioSchema.parse(invalidScenario)).toThrow();
	});

	it('should fail if ends are less than 1', () => {
		const invalidScenario = {
			title: 'A valid title',
			prologue: 'A valid prologue',
			lang: 'en-US',
			sides: [{ title: 'Side 1' }, { title: 'Side 2' }],
			firstNode: {
				title: 'First Node Title',
				text: 'First Node Text',
				author: 'Author Name'
			},
			events: [{ title: 'Event 1', text: 'Event 1 Text', author: 'Author Name' }],
			ends: []
		};

		expect(() => fullScenarioSchema.parse(invalidScenario)).toThrow();
	});
});
