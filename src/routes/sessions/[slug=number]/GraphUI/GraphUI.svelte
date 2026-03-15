<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from 'svelte-i18n';
	import nProgress from 'nprogress';
	import toast from 'svelte-french-toast';
	import * as values from '$lib/mainGraph/values';
	import {
		UserLock,
		Ellipsis,
		GitPullRequest,
		Info,
		MessageCirclePlus,
		MessageCircleWarning,
		X,
	} from 'lucide-svelte';
	import GraphTree from '../../../../components/graph/GraphTree.svelte';
	import { watch } from '$lib/runes/watch.svelte';
	import AddNode from './AddNode.svelte';
	import SelectedNode from './SelectedNode.svelte';
	import AdminPanel from './AdminPanel.svelte';
	import SessionEnd from './SessionEnd.svelte';
	import { getCurrentSessionCtx } from '$stores/session.svelte';
	import LegendDisplay from './Ledend.svelte';
	
	import type { ActionResult } from '@sveltejs/kit';
	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { RecordModel } from 'pocketbase';

	interface Props {
		graph: MainGraph | null;
		user?: RecordModel | null;
	}

	let {
		graph,
		user = null,
	}: Props = $props();

	const currentSession = getCurrentSessionCtx();

	function attributeIcons() {
		for (let s of currentSession.sides) {
			s.icon = values.graphIcons[s.number];
		}
	}
	attributeIcons();

	const states = $state({
		nodeInfo: false,
		addNode: false,
		sessionEnd: false,
		admin: false,
	});

	const stateActive = $derived.by(() => {
		return Object.values(states).some((state) => state);
	});

	let treeView = $state(false);


	/**
	 * Set the state of the UI
	 * Depending on the viewport, only one state can be active at a time
	 * @param type - The type of the state to set
	 */
	function setCheck(
		type: 'addNode' | 'nodeInfo' | 'admin' | 'sessionEnd' | 'close',
	) {
		if (type === 'close') {
			for (const key in states) {
				states[key as 'nodeInfo' | 'addNode' | 'admin' | 'sessionEnd'] =
					false;
			}
			return;
		}
		for (const key in states) {
			if (key !== type) {
				states[key as 'nodeInfo' | 'addNode' | 'admin' | 'sessionEnd'] =
					false;
			}
		}

		if (type in states) {
			states[type] = !states[type];
		}
	}

	function handleSubmit(result: ActionResult) {
		try {
			switch (result.type) {
			case 'failure':
				toast.error(result.data?.error, {
					duration: 3000,
					position: 'bottom-center',
				});
				break;
			case 'success':
				toast.success(result.data?.body.message, {
					duration: 3000,
					position: 'top-center',
				});
				states.addNode = false;

				// Add the new event to the list of events
				// TODO: need to recheck, I dont understand
				if (result.data?.body?.event && currentSession.session.expand?.events) {
					currentSession.session.expand.events.push(result.data.body.event);
				}
				break;
			default:
				break;
			}
		}
		catch (e) {
			console.error(e);
			toast.error($t('error.unknownError'), {
				duration: 3000,
				position: 'bottom-center',
			});
		}

		nProgress.done();
	}


	$effect(() => {
		watch(() => {
			if (!graph?.selectedNode) {
				states.nodeInfo = false;
				return;
			}
			if (states.nodeInfo) return;
			setCheck('nodeInfo');
		}, [graph?.selectedNode]);
	});

	onMount(async () => {
		if (graph?.selectedNode) {
			graph.selectedNode = null;
		}
		states.nodeInfo = false;
	});
</script>

<!-- Buttons -->
<div class="fixed m-4 right-0 bottom-0 z-30">
	{#snippet menuButton(type: string)}
		<!-- button to open the small menu -->
		<button
			class=" p-2 flex justify-center shadow-2xl items-center border z-50 rounded-full bg-black bg-opacity-90"
			onclick={() =>
				stateActive ? setCheck('close') : setCheck('nodeInfo')}
		>
			{#if type === 'dots'}
				<Ellipsis strokeWidth={2} color="white" />
			{:else if type === 'cross'}
				<X strokeWidth={2} color="white" />
			{/if}
		</button>
	{/snippet}
	<div class="relative h-full w-full">
		{#if stateActive}
			{@render menuButton('cross')}
			<button
				onclick={() => {
					setCheck('nodeInfo');
				}}
				class="absolute {states.nodeInfo
					? 'bg-white'
					: ''} border transition-all p-2 top-0 -translate-x-[200%] rounded-full bg-black bg-opacity-90 z-50"
			>
				<MessageCircleWarning
					strokeWidth={1.5}
					color={states.nodeInfo ? 'black' : 'white'}
				/>
			</button>
			{#if currentSession.admin.isAdmin && user && !currentSession.session.completed}
				<button
					onclick={() => {
						setCheck('admin');
					}}
					class="absolute {states.admin
						? 'bg-white'
						: ''} border p-2 top-0 -translate-x-[144%] -translate-y-[144%] rounded-full bg-black bg-opacity-90 z-50"
				>
					<UserLock
						strokeWidth={1.5}
						color={states.admin ? 'black' : 'white'}
					/>
				</button>
			{/if}
			<!-- Add Node Or Session End infos -->
			{#if currentSession.session.end && currentSession.session.completed}
				<button
					onclick={() => {
						setCheck('sessionEnd');
					}}
					class="absolute {states.sessionEnd
						? 'bg-white'
						: ''} border p-2 top-0 -translate-y-[200%] rounded-full bg-black bg-opacity-90 z-50"
				>
					<Info
						strokeWidth={1.5}
						color={states.sessionEnd ? 'black' : 'white'}
					/>
				</button>
			{:else}
				<button
					onclick={() => {
						setCheck('addNode');
					}}
					class="absolute {states.addNode
						? 'bg-white'
						: ''} border p-2 top-0 -translate-y-[200%] rounded-full bg-black bg-opacity-90 z-50"
				>
					<MessageCirclePlus
						strokeWidth={1.5}
						color={states.addNode ? 'black' : 'white'}
					/>
				</button>
			{/if}
		{:else}
			{@render menuButton('dots')}
		{/if}
	</div>
</div>

<LegendDisplay />

<!-- Display -->
{#if stateActive}
	<!-- affichage détails message -->
	{#if states.nodeInfo}
		<SelectedNode {graph} />
	{:else if states.addNode && !currentSession.session.completed}
		<AddNode
			{graph}
			{handleSubmit}
		/>
	{:else if states.admin && !currentSession.session.completed}
		<AdminPanel
			{handleSubmit}
		/>
	{:else if states.sessionEnd}
		<SessionEnd />
	{/if}
{/if}

<!-- Graph Tree -->
<div class=" fixed m-4 left-0 top-16 z-30">
	<button
		class="p-2 flex justify-center shadow-2xl items-center border border-white rounded-full bg-black bg-opacity-90"
		onclick={() => (treeView = !treeView)}
	>
		<GitPullRequest strokeWidth={1.5} color="white" />
	</button>
	{#if treeView}
		<GraphTree {graph} />
	{/if}
</div>
