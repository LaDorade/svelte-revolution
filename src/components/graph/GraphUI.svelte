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
	import GraphTree from './GraphTree.svelte';
	import { watch } from '$lib/runes/watch.svelte';
	import { pb } from '$lib/client/pocketbase';
	import AddNode from './GraphUI/AddNode.svelte';
	import SelectedNode from './GraphUI/SelectedNode.svelte';
	
	import type {
		End,
		GraphEvent,
		Session,
		Side,
	} from '$types/pocketBase/TableTypes';
	import type { ActionResult } from '@sveltejs/kit';
	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { RecordModel } from 'pocketbase';
	import AdminPanel from './GraphUI/AdminPanel.svelte';
	import SessionEnd from './GraphUI/SessionEnd.svelte';

	interface Props {
		graph: MainGraph | null;
		session: Session;
		user?: RecordModel | null;
		admin?: boolean;
		events?: GraphEvent[];
		ends?: End[];
		sides: Side[];
		pseudo: string | null;
		userSideId: string | null;
	}

	let {
		graph,
		user = null,
		session = $bindable(),
		admin = false,
		events = [],
		ends = [],
		sides,
		pseudo,
		userSideId = $bindable(),
	}: Props = $props();

	function attributeIcons() {
		for (let s of sides) {
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
				if (result.data?.body?.event && session.expand?.events) {
					session.expand.events.push(result.data.body.event);
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

	async function handleSessionEnd() {
		// Listen for session completion
		await pb.collection('Session').subscribe(session.id, async (res) => {
			if (!res.record || !res.record.completed) return;
			try {
				const end = await pb
					.collection('End')
					.getOne(res.record.end ?? '');
				session.completed = res.record.completed;
				session.end = res.record.end;
				setCheck('sessionEnd');
				session.expand = session.expand
					? {
						...session.expand,
						...end,
					}
					: {};
				toast.success($t('sessions.sessionIsOver'), {
					position: 'top-left',
				});
			} catch (e) {
				console.error(e);
			}
		});
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
		await handleSessionEnd();
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
			{#if admin && user && !session.completed}
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
			{#if session.end && session.completed}
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

<!-- Sides legend -->
<div
	class="fixed max-h-3/4 overflow-y-auto z-40 rounded-xl shadow-2xl p-4 bottom-0 left-0 bg-black bg-opacity-30"
>
	{#each sides as side (side.id)}
		<div class="text-white flex items-center">
			<svg class="w-4 h-4 mr-1" viewBox="-12 -12 24 24">
				<path d={side.icon} fill="white" />
			</svg>
			{side.name}
		</div>
	{/each}
</div>

<!-- Display -->
{#if stateActive}
	<!-- affichage détails message -->
	{#if states.nodeInfo}
		<SelectedNode {graph} {sides} {pb} />
	{:else if states.addNode && !session.completed}
		<AddNode
			{graph}
			{handleSubmit}
			{admin}
			{sides}
			{pseudo}
			{userSideId}
			{session}
		/>
	{:else if states.admin && !session.completed}
		<AdminPanel
			{session}
			{pb}
			{handleSubmit}
			{ends}
			{events}
		/>
	{:else if states.sessionEnd}
		<SessionEnd
			{session}
		/>
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
