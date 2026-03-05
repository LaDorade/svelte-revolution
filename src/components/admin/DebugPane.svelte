<script lang="ts">
	import { pb } from '$lib/client/pocketbase';
	import { ClientResponseError } from 'pocketbase';
	import toast from 'svelte-french-toast';
	import { Pane, Button, Text, Textarea, Separator, ThemeUtils, type Theme } from 'svelte-tweakpane-ui';
	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { Session } from '$types/pocketBase/TableTypes';

	let { graph, session }: { graph: MainGraph | null; session: Session } = $props();

	let nodeModification = $state(false);
	let nodeDeletion = $state(false);

	const customizedTheme: Theme = {
		...ThemeUtils.presets.retro,
		inputBackgroundColor: '#000',
		baseBackgroundColor: '#000',
		labelForegroundColor: '#fff',
		buttonBackgroundColor: '#222',
		buttonForegroundColor: '#fff'
	};

	function checkAuth() {
		if (session.author === pb.authStore.record?.id || pb.authStore.record?.role === 'superAdmin') {
			return;
		}
		throw new Error('Not authenticated');
	}

	async function addRandomNode() {
		const { faker } = await import('@faker-js/faker/locale/fr');
		faker.seed(new Date().getTime());
		try {
			if (!graph) {
				throw new Error('No graph');
			}
			if (!graph?.selectedNode) {
				throw new Error('No selected node');
			}
			checkAuth();
			// génère des données aléatoires
			const data = {
				title: faker.animal.fish(),
				text: faker.internet.displayName() + '! ' + faker.science.chemicalElement().name + '!',
				type: 'contribution',
				author: faker.music.songName() + ' from ' + faker.music.artist(),
				parent: graph?.selectedNode?.id,
				session: graph?.selectedNode?.session
			};

			const node = await pb.collection('Node').create(data);
			graph.selectedNode = node;
		} catch (e) {
			console.error(e);
			const err = e as ClientResponseError;
			toast.error(err.message);
		}
	}

	async function updateNode() {
		if (!graph?.selectedNode) {
			return;
		}
		try {
			if (graph) {
				checkAuth();
				const id = String(graph?.selectedNode.id);
				const data = {
					title: graph?.selectedNode.title,
					text: graph?.selectedNode.text
				};
				// graph.selectedNode = null;
				await pb.collection('Node').update(id, data);
				toast.success('Node updated');
				nodeModification = false;
			}
		} catch (e) {
			const err = e as ClientResponseError;
			toast.error(err.message);
		}
	}

	async function deleteNode() {
		try {
			if (graph?.selectedNode?.type === 'startNode') {
				throw new Error('Cannot delete start node');
			}
			checkAuth();
			const newParent = graph?.selectedNode?.parent;
			if (!newParent) {
				throw new Error('No parent');
			}
			const nodes = await pb
				.collection('Node')
				.getFullList({ filter: `parent="${String(graph?.selectedNode?.id)}"` });

			const promiseList = nodes.map(async (node) => {
				return pb.collection('Node').update(String(node.id), { parent: newParent });
			});
			await Promise.all(promiseList);
			await pb.collection('Node').delete(String(graph?.selectedNode?.id));
			toast.success('Node deleted');
			nodeDeletion = false;
		} catch (e) {
			const err = e as ClientResponseError;
			toast.error(err.message);
		}
	}
</script>

<Pane position="draggable" title="Debug Panel" theme={customizedTheme}>
	{#if graph}
		<Button
			on:click={() => {
				const randomIndex = Math.floor(Math.random() * graph?._nodes.length);
				if (graph?._nodes[randomIndex]) {
					graph.selectedNode = graph._nodes[randomIndex];
				}
			}}
			title="Select Random Node"
		></Button>
		<Button on:click={addRandomNode} title="Add random node"></Button>
		<Separator />
		<Button on:click={() => (nodeDeletion = graph?.selectedNode ? !nodeDeletion : false)} title="Delete node"
		></Button>
		{#if nodeDeletion && graph?.selectedNode}
			<Button on:click={() => (nodeDeletion = false)} title="Cancel deletion"></Button>
			<Button on:click={deleteNode} title="Confirm deletion"></Button>
		{/if}
		<Separator />
		{#if graph?.selectedNode}
			<Text on:change={() => (nodeModification = true)} bind:value={graph.selectedNode.title} label="Node title"
			></Text>
			<Textarea
				on:change={() => (nodeModification = true)}
				bind:value={graph.selectedNode.text}
				label="Node description"
			></Textarea>
			<Text disabled value={String(graph?.selectedNode.id)} label="Node ID"></Text>
			<Text disabled value={String(graph?.selectedNode.parent)} label="Parent ID"></Text>
			<Button on:click={updateNode} title="Update node"></Button>
			{#if nodeModification}
				<Text disabled value="Change not saved !" label="Status"></Text>
			{/if}
		{/if}
	{:else}
		<Text value="No graph" label="Status"></Text>
	{/if}
</Pane>
