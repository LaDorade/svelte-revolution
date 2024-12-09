import { createGraphStore } from '$stores/graph/index.svelte';
import type { BaseNode } from '$types/graph';

interface ExampleNode extends d3.SimulationNodeDatum, BaseNode {}

const exampleNodes: ExampleNode[] = [
	{
		id: 1,
		title: 'home.exampleGraph.title1',
		text: 'home.exampleGraph.text1'
	},
	{
		id: 2,
		title: 'home.exampleGraph.title2',
		text: 'home.exampleGraph.text2'
	},
	{
		id: 3,
		title: 'home.exampleGraph.title3',
		text: 'home.exampleGraph.text3'
	},
	{
		id: 4,
		title: 'home.exampleGraph.title4',
		text: 'home.exampleGraph.text4'
	},
	{
		id: 5,
		title: 'home.exampleGraph.title5',
		text: 'home.exampleGraph.text5'
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
