import { createGraphStore } from '$stores/graph/index.svelte';
import type { BaseNode } from '$types/graph';

interface ExampleNode extends d3.SimulationNodeDatum, BaseNode {}

const exampleNodes: ExampleNode[] = [
	{
		id: 1,
		title: 'exampleGraph.title1',
		text: 'exampleGraph.text1'
	},
	{
		id: 2,
		title: 'exampleGraph.title2',
		text: 'exampleGraph.text2'
	},
	{
		id: 3,
		title: 'exampleGraph.title3',
		text: 'exampleGraph.text3'
	},
	{
		id: 4,
		title: 'exampleGraph.title4',
		text: 'exampleGraph.text4'
	},
	{
		id: 5,
		title: 'exampleGraph.title5',
		text: 'exampleGraph.text5'
	}
];

const links = [
	{ source: 1, target: 2 },
	{ source: 1, target: 3 },
	{ source: 2, target: 4 },
	{ source: 3, target: 5 }
];

const homeStore = createGraphStore(exampleNodes, links);

export { homeStore, type ExampleNode };
