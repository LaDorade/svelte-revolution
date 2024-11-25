<script lang="ts">
	import { goto } from '$app/navigation';
	import { pb } from '$lib/client/pocketbase';
	import { ClientResponseError } from 'pocketbase';
	import toast from 'svelte-french-toast';
	import { Pane, Button, Text, Textarea, Separator, TabGroup, TabPage, FpsGraph } from 'svelte-tweakpane-ui';
	import { linksStore, nodesStore } from '$stores/graph';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';

	let nodeUpdated = $state(false);

	function checkAuth() {
		pb.authStore.loadFromCookie(document.cookie);
		if (!pb.authStore.isValid || pb.authStore.model?.role !== 'superAdmin') {
			throw new Error('Not authenticated');
		}
	}

	async function addRandomNode() {
		const { faker } = await import('@faker-js/faker/locale/fr');
		faker.seed(new Date().getTime());
		try {
			checkAuth();
			// génère des données aléatoires
			const data = {
				title: faker.animal.fish(),
				text: faker.internet.displayName() + '! ' + faker.science.chemicalElement().name + '!',
				type: 'contribution',
				author: faker.music.songName() + ' from ' + faker.music.artist(),
				parent: mainGraphStore.selectedNode?.id,
				session: mainGraphStore.selectedNode?.session
			};

			const node = await pb.collection('Node').create(data);
			mainGraphStore.selectedNode = node;
		} catch (e) {
			console.error(e);
			const err = e as ClientResponseError;
			toast.error(err.message);
		}
	}

	async function updateNode() {
		if (!mainGraphStore.selectedNode) {
			return;
		}
		try {
			checkAuth();
			const id = String(mainGraphStore.selectedNode.id);
			const data = {
				title: mainGraphStore.selectedNode.title,
				text: mainGraphStore.selectedNode.text
			};
			mainGraphStore.selectedNode = null;
			await pb.collection('Node').update(id, data);
			toast.success('Node updated');
			nodeUpdated = false;
		} catch (e) {
			const err = e as ClientResponseError;
			toast.error(err.message);
		}
	}

	async function deleteNode() {
		try {
			if (mainGraphStore.selectedNode?.type === 'startNode') {
				throw new Error('Cannot delete start node');
			}
			checkAuth();
			const newParent = mainGraphStore.selectedNode?.parent;
			if (!newParent) {
				throw new Error('No parent');
			}
			const nodes = await pb
				.collection('Node')
				.getFullList({ filter: `parent="${String(mainGraphStore.selectedNode?.id)}"` });

			const promiseList = nodes.map(async (node) => {
				return pb.collection('Node').update(String(node.id), { parent: newParent });
			});
			await Promise.all(promiseList);
			await pb.collection('Node').delete(String(mainGraphStore.selectedNode?.id));
			toast.success('Node deleted');
		} catch (e) {
			const err = e as ClientResponseError;
			toast.error(err.message);
		}
	}
</script>

<Pane position="draggable" title="Debug Panel">
	<TabGroup>
		<Separator />
		<TabPage title="Basics">
			<Button on:click={() => goto('/roadmap')} title="Go to Tasks"></Button>
			<Button on:click={() => window.location.reload()} title="Reload Page"></Button>
			{#if $nodesStore.length && $linksStore.length}
				<Button
					on:click={() => {
						const randomIndex = Math.floor(Math.random() * $nodesStore.length);
						mainGraphStore.selectedNode = $nodesStore[randomIndex];
					}}
					title="Select Random Node"
				></Button>
			{/if}
			<FpsGraph interval={50} label="FPS" rows={3} />
		</TabPage>
		{#if $nodesStore.length && $linksStore.length && mainGraphStore.selectedNode}
			<TabPage selected={!!mainGraphStore.selectedNode} title="Graph">
				<Button on:click={addRandomNode} title="Add random node"></Button>
				<Separator />
				<Button on:click={deleteNode} title="Delete node"></Button>
				<Separator />
				<Text
					on:change={() => (nodeUpdated = true)}
					bind:value={mainGraphStore.selectedNode.title}
					label="Node title"
				></Text>
				<Textarea
					on:change={() => (nodeUpdated = true)}
					bind:value={mainGraphStore.selectedNode.text}
					label="Node description"
				></Textarea>
				<Text disabled value={String(mainGraphStore.selectedNode.id)} label="Node ID"></Text>
				<Text disabled value={String(mainGraphStore.selectedNode.parent)} label="Parent ID"></Text>
				<Button on:click={updateNode} title="Update node"></Button>
				{#if nodeUpdated}
					<Text disabled value="Change not saved !" label="Status"></Text>
				{/if}
			</TabPage>
		{/if}
	</TabGroup>
</Pane>
