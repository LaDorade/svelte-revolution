<script lang="ts">
	import { onMount } from 'svelte';
	import { t } from 'svelte-i18n';
	import type { End, GraphEvent, Session, Side, User } from '$types/pocketBase/TableTypes';
	import { applyAction, enhance } from '$app/forms';
	import nProgress from 'nprogress';
	import toast from 'svelte-french-toast';
	import type { ActionResult } from '@sveltejs/kit';
	import { blur, fade, slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import * as values from '$lib/mainGraph/values';
	import {
		Codesandbox,
		Ellipsis,
		GitPullRequest,
		Info,
		MessageCirclePlus,
		MessageCircleWarning,
		X
	} from 'lucide-svelte';
	import GraphTree from './GraphTree.svelte';
	import { watch } from '$lib/runes/watch.svelte';
	import { pb } from '$lib/client/pocketbase';
	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { RecordModel } from 'pocketbase';
	import { viewportStore } from '$stores/ui/index.svelte';

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
		userSideId = $bindable()
	}: Props = $props();

	function attributeIcons() {
		for (let s of sides) {
			s.icon = values.graphIcons[s.number];
		}
	}
	attributeIcons();

	let nodeTitle = $state('');
	let nodeText = $state('');
	let ai = $derived.by(() => session.expand?.scenario?.ai);

	const states = $state({
		nodeInfo: false,
		addNode: false,
		sessionEnd: false,
		admin: false
	});

	const stateActive = $derived.by(() => {
		return Object.values(states).some((state) => state);
	});

	let treeView = $state(false);

	function storePanelInLocalStorage() {
		localStorage.setItem('seeDebugPanel', viewportStore.seeDebugPanel.toString());
	}

	/**
	 * Set the state of the UI
	 * Depending on the viewport, only one state can be active at a time
	 * @param type - The type of the state to set
	 */
	function setCheck(type: 'addNode' | 'nodeInfo' | 'admin' | 'sessionEnd' | 'close') {
		if (type === 'close') {
			for (const key in states) {
				states[key as 'nodeInfo' | 'addNode' | 'admin' | 'sessionEnd'] = false;
			}
			return;
		}
		for (const key in states) {
			if (key !== type) {
				states[key as 'nodeInfo' | 'addNode' | 'admin' | 'sessionEnd'] = false;
			}
		}

		if (type in states) {
			states[type] = !states[type];
		}
	}

	function handleSubmit(result: ActionResult) {
		switch (result.type) {
			case 'failure':
				toast.error(result.data?.error, { duration: 3000, position: 'bottom-center' });
				break;
			case 'success':
				toast.success(result.data?.body.message, { duration: 3000, position: 'top-center' });
				states.addNode = false;
				nodeTitle = '';
				nodeText = '';

				// Add the new event to the list of events
				if (result.data?.body?.event && session.expand?.events) {
					session.expand.events.push(result.data.body.event);
				}
				break;
			default:
				break;
		}
		nProgress.done();
	}

	async function handleSessionEnd() {
		// Listen for session completion
		await pb.collection('Session').subscribe(session.id, async (res) => {
			if (!res.record || !res.record.completed) return;
			try {
				const end = await pb.collection('End').getOne(res.record.end ?? '');
				session.completed = res.record.completed;
				session.end = res.record.end;
				setCheck('sessionEnd');
				session.expand = session.expand
					? {
							...session.expand,
							...end
						}
					: {};
				toast.success($t('sessions.sessionIsOver'), {
					position: 'top-left'
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

{#snippet formTemplate(values: { id: string; title: string }[], action: string, name: string, trad: string)}
	<form
		method="POST"
		action="/sessions/{session.id}?/{action}"
		onsubmit={(e) => {
			e.preventDefault();
		}}
		use:enhance={() => {
			nProgress.start();
			return async ({ result }) => {
				handleSubmit(result);
			};
		}}
		class="flex flex-col gap-2 p-x-4 cursor-default text-primary-500 w-full items-center"
	>
		<label class="form-control w-full max-w-xs">
			<select {name} id={name} class="bg-black rounded-md">
				<option disabled selected>{trad}</option>
				{#each values as value}
					<option value={value.id}>{value.title}</option>
				{/each}
			</select>
		</label>
		<input type="hidden" name="session" value={session.id} />
		<input type="hidden" name="pb_cookie" value={pb.authStore.exportToCookie()} />
		<button type="submit" class="self-center btn btn-sm btn-accent">
			{trad}
		</button>
	</form>
{/snippet}

<!-- Buttons -->
<div class="fixed m-4 right-0 bottom-0 z-50">
	{#snippet menuButton(type: string)}
		<!-- button to open the small menu -->
		<button
			class=" p-2 flex justify-center shadow-2xl items-center border z-50 rounded-full bg-black bg-opacity-90"
			onclick={() => (stateActive ? setCheck('close') : setCheck('nodeInfo'))}
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
				<MessageCircleWarning strokeWidth={1.5} color={states.nodeInfo ? 'black' : 'white'} />
			</button>
			{#if admin && user}
				<button
					onclick={() => {
						setCheck('admin');
					}}
					class="absolute {states.admin
						? 'bg-white'
						: ''} border p-2 top-0 -translate-x-[144%] -translate-y-[144%] rounded-full bg-black bg-opacity-90 z-50"
				>
					<Codesandbox strokeWidth={1.5} color={states.admin ? 'black' : 'white'} />
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
					<Info strokeWidth={1.5} color={states.sessionEnd ? 'black' : 'white'} />
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
					<MessageCirclePlus strokeWidth={1.5} color={states.addNode ? 'black' : 'white'} />
				</button>
			{/if}
		{:else}
			{@render menuButton('dots')}
		{/if}
	</div>
</div>

<!-- Sides legend -->
<div class="fixed max-h-3/4 overflow-y-auto z-40 rounded-xl shadow-2xl p-4 bottom-0 left-0 bg-black bg-opacity-30">
	{#each sides as side}
		<div class="text-white flex items-center">
			<img src={side.icon} alt={'icon'} class="w-4 h-4 mr-1 filter invert" draggable="false" />
			{side.name}
		</div>
	{/each}
</div>

<!-- Display -->
{#if stateActive}
	<!-- affichage détails message -->
	<div
		class="fixed w-1/2 max-h-3/4 overflow-y-auto z-40 rounded-xl shadow-2xl
			p-2 m-4 bottom-0 left-0 bg-black bg-opacity-75"
		transition:fade={{ duration: 200 }}
	>
		{#if states.nodeInfo}
			<div in:fade={{ duration: 200, easing: quintOut }}>
				{#if graph?.selectedNode}
					{#key graph?.selectedNode}
						<div
							in:blur={{
								duration: 300,
								easing: quintOut,
								amount: 2,
								opacity: 0.4
							}}
							class="flex flex-col items-center gap-2"
						>
							<div class="text-xl text-white font-semibold first-letter:capitalize">
								{graph?.selectedNode.title}
							</div>
							<div class="text-green-400 flex items-center">
								{#if graph?.selectedNode?.side}
									<img
										src={sides.find((side) => side.id === graph?.selectedNode?.side)?.icon}
										alt={'icon'}
										class="w-4 h-4 mr-1 filter invert"
										style={'filter: invert(51%) sepia(73%) saturate(352%) hue-rotate(90deg);'}
									/>
								{/if}
								{sides.find((side) => side.id === graph?.selectedNode?.side)?.name}
							</div>
							<div>
								{$t('inSession.from')}
								<span class="text-white">{graph?.selectedNode.author}</span>
							</div>
							<div class="max-h-60 overflow-auto text-justify text-gray-300">
								{@html graph?.selectedNode.text}
							</div>
						</div>
					{/key}
				{:else}
					<div class="text-xl text-center font-semibold first-letter:capitalize">
						{$t('inSession.noNodeSelected')}
					</div>
				{/if}
			</div>
		{:else if states.addNode && !session.completed}
			<form
				in:fade={{ duration: 200 }}
				method="POST"
				action="/sessions/{session.slug}?/addNode"
				class="flex flex-col items-center gap-2 cursor-default p-2 z-10 w-full"
				onsubmit={(e) => {
					e.preventDefault();
				}}
				use:enhance={() => {
					nProgress.start();
					if (!graph?.selectedNode) {
						toast.error($t('inSession.noNodeSelected'), { duration: 3000, position: 'bottom-center' });
						nProgress.done();
						return;
					}
					return async ({ result }) => {
						applyAction(result);
						handleSubmit(result);
						nProgress.done();
					};
				}}
			>
				<label class="form-control w-full max-w-xs">
					<div class="label p-0">
						<span class="label-text text-inherit">{$t('home.messageTitle')}</span>
					</div>
					<input
						name="title"
						type="text"
						bind:value={nodeTitle}
						placeholder="Youhouhou"
						class="input input-sm input-accent text-primary-500 bg-gray-950 input-bordered w-full max-w-xs"
					/>
				</label>
				<label class="form-control w-full max-w-xs">
					<div class="label p-0">
						<span class="label-text text-inherit">{$t('home.yourMessage')}</span>
					</div>
					<textarea
						name="text"
						bind:value={nodeText}
						class="textarea textarea-accent text-primary-500 bg-gray-950"
						placeholder="Ton message"
					></textarea>
				</label>
				{#if admin}
					<label class="form-control w-full max-w-xs">
						<div class="label p-0">
							<span class="label-text text-inherit">{$t('side.yourSide')}</span>
						</div>
						<select bind:value={userSideId} name="side" class="text-primary-500">
							<option value={null} disabled selected>{$t('side.chooseSide')}</option>
							{#each sides as side}
								<option value={side.id}>{side.name}</option>
							{/each}
						</select>
					</label>
				{:else}
					<input type="hidden" name="side" value={userSideId} />
					<div class=" flex gap-2">
						<div class="">
							{$t('side.yourSide')} :
						</div>
						<div class=" text-white">
							{sides.find((side) => side.id === userSideId)?.name}
						</div>
					</div>
				{/if}
				{#if !admin}
					<div class=" flex gap-2">
						<div>
							{$t('home.yourName')} :
						</div>
						<div class=" text-white">
							{pseudo}
						</div>
					</div>
					<input
						value={pseudo}
						name="author"
						type={'hidden'}
						placeholder="Pseudo"
						class="input input-sm input-accent text-primary-500 bg-gray-950 input-bordered w-full max-w-xs"
					/>
				{:else}
					<label class="form-control w-full max-w-xs">
						<div class="label p-0">
							<span class="label-text text-inherit">{$t('home.yourName')}</span>
						</div>
						<input
							value={pseudo}
							name="author"
							type={'text'}
							placeholder="Pseudo"
							class="input input-sm input-accent text-primary-500 bg-gray-950 input-bordered w-full max-w-xs"
						/>
					</label>
				{/if}
				<input type="hidden" name="session" value={session.id} />
				<input type="hidden" name="parent" value={graph?.selectedNode?.id ?? null} />
				<button class="btn w-fit btn-accent btn-sm self-center" type="submit">{$t('misc.submit')}</button>
			</form>
		{:else if states.admin}
			<div
				in:fade={{
					duration: 200,
					easing: quintOut
				}}
				class="flex flex-col items-center gap-4 p-2 text-primary-500 z-10"
			>
				<div>
					<label>
						{$t('admin.debugPanel')}
						<input
							class=" cursor-pointer"
							type="checkbox"
							name="seeDebugPane"
							id="debugPaneCheck"
							onchange={storePanelInLocalStorage}
							bind:checked={viewportStore.seeDebugPanel}
						/>
					</label>
				</div>
				{@render formTemplate(events, 'addEvent', 'eventId', $t('admin.event.triggerEvent'))}
				{@render formTemplate(ends, 'endSession', 'endId', $t('admin.session.endSession'))}
			</div>
		{:else if states.sessionEnd}
			<div
				in:fade={{
					duration: 200,
					easing: quintOut
				}}
				class="flex flex-col items-center gap-2 p-2 text-primary-500 z-10"
			>
				<div class="text-xl font-semibold text-white first-letter:capitalize">
					{session.expand?.end?.title}
				</div>
				<div>
					{session.expand?.end?.text}
				</div>
			</div>
		{/if}
	</div>
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
