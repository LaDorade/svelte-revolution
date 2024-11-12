<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { t } from 'svelte-i18n';
	import type { End, GraphEvent, Session, Side, User } from '$types/pocketBase/TableTypes';
	import { selectedNodeStore } from '$stores/graph';
	import { enhance } from '$app/forms';
	import nProgress from 'nprogress';
	import toast from 'svelte-french-toast';
	import type { ActionResult } from '@sveltejs/kit';
	import { blur, fade, slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { Codesandbox, Ellipsis, Info, MessageCirclePlus, X } from 'lucide-svelte';

	interface Props {
		session: Session;
		user?: User | null;
		admin?: boolean;
		events?: GraphEvent[];
		ends?: End[];
		sides?: Side[];
	}

	let { user = null, session, admin = false, events = [], ends = [], sides = [] }: Props = $props();

	let nodeTitle = $state('');
	let nodeText = $state('');
	let nodeAuthor = $state('');

	let theForm: HTMLFormElement | undefined = $state();
	let validForm = $state(false);

	const states = $state({
		nodeInfo: false,
		addNode: false,
		sessionEnd: false,
		admin: false
	});

	const stateActive = $derived.by(() => {
		return Object.values(states).some((state) => state);
	});

	/**
	 * Set the state of the UI
	 * Depending on the viewport, only one state can be active at a time
	 * @param type - The type of the state to set
	 */
	function setCheck(type: 'addNode' | 'nodeInfo' | 'admin') {
		for (const key in states) {
			if (key !== type) {
				states[key as 'nodeInfo' | 'addNode' | 'admin'] = false;
			}
		}

		if (type in states) {
			states[type] = !states[type];
		}
	}

	function handleActionResult(result: ActionResult) {
		switch (result.type) {
			case 'failure':
				toast.error(result.data?.error, { duration: 3000, position: 'bottom-center' });
				break;
			case 'success':
				toast.success(result.data?.body.message, { duration: 3000, position: 'top-center' });
				states.addNode = false;
				nodeTitle = '';
				nodeText = '';
				localStorage.setItem('author', nodeAuthor);

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

	const selectedNodeUnsubscribe = selectedNodeStore.subscribe((value) => {
		if (!value) {
			states.nodeInfo = false;
			return;
		}
		if (states.nodeInfo) return;
		setCheck('nodeInfo');
	});

	onMount(() => {
		nodeAuthor = localStorage.getItem('author') || '';
		selectedNodeStore.set(null);
		states.nodeInfo = false;
	});

	onDestroy(() => {
		selectedNodeUnsubscribe();
	});
</script>

<!-- 
<div class="z-50 border-t border-gray-500 divide-x divide-gray-500 bg-black bg-opacity-25 btm-nav">
	<!-- Add Node Or Session Ended ->
	{#if !session?.completed}
		<div class="flex flex-col-reverse">
			<button
				type="button"
				class="z-20 flex flex-col items-center justify-center w-full h-full"
				onclick={() => {
					setCheck('addNode');
				}}
			>
				<MessageCirclePlus strokeWidth={1.5} />
				<span class="text-sm font-light">{$t('sessions.addNode')}</span>
			</button>
			<!-- Menu for Add Node ->
			{#if states.addNode}
				<form
					transition:slide={{
						duration: 200,
						easing: quintOut
					}}
					method="post"
					action="/sessions/{session.id}?/addNode"
					class="flex flex-col items-center gap-2 cursor-default p-2 absolute z-10 w-screen left-0 md:w-full bg-gray-950 border-t opacity-90 bottom-full"
					onsubmit={(e) => {
						e.preventDefault();
						if (theForm) {
							validForm = theForm.checkValidity();
							if (validForm) {
								theForm.requestSubmit();
							}
						}
					}}
					use:enhance={() => {
						nProgress.start();
						return async ({ update, result }) => {
							await update({ reset: false });
							handleActionResult(result);
							nProgress.done();
						};
					}}
				>
					<label class="form-control w-full max-w-xs">
						<div class="label p-0">
							<span class="label-text text-inherit">{$t('messageTitle')}</span>
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
							<span class="label-text text-inherit">{$t('yourName')}</span>
						</div>
						<input
							name="author"
							type="text"
							bind:value={nodeAuthor}
							placeholder="Snoup"
							class="input input-sm input-accent text-primary-500 bg-gray-950 input-bordered w-full max-w-xs"
						/>
					</label>
					<label class="form-control w-full max-w-xs">
						<div class="label p-0">
							<span class="label-text text-inherit">{$t('side.yourSide')}</span>
						</div>
						<select
							name="side"
							class="select select-accent text-primary-500 bg-gray-950 select-sm select-bordered"
						>
							{#each sides as side}
								<option value={side.id}>{side.name}</option>
							{/each}
						</select>
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
					<input type="hidden" name="session" value={session.id} />
					<input type="hidden" name="parent" value={$selectedNodeStore?.id ?? null} />
					<button class="btn w-fit btn-accent btn-sm self-center" type="submit">{$t('form.submit')}</button>
				</form>
			{/if}
		</div>
	{:else}
		<div class="flex flex-col-reverse">
			<!-- Session End ->
			<button
				type="button"
				class="z-20 flex flex-col items-center justify-center w-full h-full bg-gray-950"
				onclick={() => {
					setCheck('sessionEnd');
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-5 h-5"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M5 12l5-5m0 0l5 5m-5-5v12"
					/>
				</svg>
				<span class="btm-nav-label">{$t('sessions.sessionEnded')}</span>
			</button>
			{#if states.sessionEnd}
				<div
					transition:slide={{
						duration: 200,
						easing: quintOut
					}}
					class="flex flex-col items-center gap-2 p-2 absolute z-10 left-0 w-screen md:w-full bg-gray-950 border-t opacity-90 bottom-full cursor-default"
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
	<!-- Node Info button ->
	<div class="flex flex-row-reverse">
		<button
			type="button"
			class="z-20 flex flex-col items-center justify-center w-full h-full"
			onclick={() => {
				setCheck('nodeInfo');
			}}
		>
			<Info strokeWidth={1.5} />
			<span class="text-sm font-light">{$t('nodeInformation')}</span>
		</button>
		{#if states.nodeInfo}
			<div
				transition:slide|global={{
					duration: 200,
					easing: quintOut
				}}
				class="p-2 text-primary-500 absolute z-10 w-screen md:w-full bg-gray-950 border-t opacity-90 bottom-full {admin
					? ''
					: 'right-0'}"
			>
				{#if $selectedNodeStore}
					{#key $selectedNodeStore}
						<div
							in:blur={{
								duration: 800,
								easing: quintOut,
								amount: 2,
								opacity: 0.4
							}}
							class="flex flex-col items-center gap-2"
						>
							<div class="text-xl text-white font-semibold first-letter:capitalize">
								{$selectedNodeStore.title}
							</div>
							<div>
								{$t('from')}
								<span class="text-white">{$selectedNodeStore.author}</span>
							</div>
							<div class="max-h-60 overflow-auto text-justify text-gray-300">
								{$selectedNodeStore.text}
							</div>
						</div>
					{/key}
				{:else}
					<div class="text-xl text-center font-semibold first-letter:capitalize">
						{$t('noNodeSelected')}
					</div>
				{/if}
			</div>
		{/if}
	</div>
	<!-- Admin button (visible only for admins) ->
	{#if admin && user && !session?.completed}
		<div class="flex flex-col-reverse">
			<button
				type="button"
				class="z-20 flex flex-col items-center justify-center w-full h-full bg-gray-950"
				onclick={() => {
					setCheck('admin');
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="w-5 h-5"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v8m4-4H8" />
				</svg>
				<span class="btm-nav-label">{$t('admin')}</span>
			</button>
			{#if states.admin}
				<div
					transition:slide={{
						duration: 200,
						easing: quintOut
					}}
					class="flex flex-col items-center gap-2 p-2 text-primary-500 absolute z-10 w-screen right-0 md:w-full bg-gray-950 border-t opacity-90 bottom-full cursor-default"
				>
					{@render formTemplate(events, 'event', 'event', $t('sessions.addEvent'), true)}
					{@render formTemplate(ends, 'end', 'end', $t('sessions.endSession'))}
				</div>
			{/if}
		</div>
	{/if}
</div> -->

{#snippet formTemplate(
	values: { id: string; title: string }[],
	action: string,
	name: string,
	trad: string,
	needDisabled: boolean = false
)}
	<form
		method="POST"
		action="/sessions/{session.id}?/{action}"
		onsubmit={(e) => e.preventDefault()}
		use:enhance={() => {
			nProgress.start();
			return async ({ update, result }) => {
				await update();
				handleActionResult(result);
			};
		}}
		class="flex flex-col gap-4 p-x-4 cursor-default text-primary-500 w-full items-center"
	>
		<label class="form-control w-full max-w-xs">
			<div class="label">
				<span class="label-text text-inherit">{trad}</span>
			</div>
			<select {name} id={name} class="select select-accent appearance-none bg-black select-sm">
				<option disabled selected>{trad}</option>
				{#each values as value}
					{@const alreadySelected =
						needDisabled &&
						(session.expand?.events?.filter((event) => event.id === value.id).length ?? 0) > 0}
					<option disabled={alreadySelected} value={value.id}>{value.title}</option>
				{/each}
			</select>
		</label>

		<input type="hidden" name="session" value={session.id} />
		<button type="submit" class="self-center btn btn-sm btn-accent">
			{trad}
		</button>
	</form>
{/snippet}

<!-- Buttons -->
<div class="fixed m-4 right-0 bottom-0 z-50">
	{#snippet menuButton(type: string)}
		<button
			class=" p-2 flex justify-center shadow-2xl items-center border z-50 rounded-full bg-black bg-opacity-90"
			onclick={() => (states.nodeInfo = !states.nodeInfo)}
		>
			{#if type === 'dots'}
				<Ellipsis strokeWidth={1.5} color="white" />
			{:else if type === 'cross'}
				<X strokeWidth={1.5} color="white" />
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
				class="absolute border transition-all p-2 top-0 -translate-x-[200%] rounded-full bg-black bg-opacity-90 z-50"
			>
				<Info strokeWidth={1.5} color="white" />
			</button>
			<button
				onclick={() => {
					setCheck('admin');
				}}
				class="absolute border p-2 top-0 -translate-x-[144%] -translate-y-[144%] rounded-full bg-black bg-opacity-90 z-50"
			>
				<Codesandbox strokeWidth={1.5} color="white" />
			</button>
			<button
				onclick={() => {
					setCheck('addNode');
				}}
				class="absolute border p-2 top-0 -translate-y-[200%] rounded-full bg-black bg-opacity-90 z-50"
			>
				<MessageCirclePlus color="white" strokeWidth={1.5} />
			</button>
		{:else}
			{@render menuButton('dots')}
		{/if}
	</div>
</div>

<!-- Display -->
{#if stateActive}
	<div
		class="fixed w-1/2 max-h-3/4 overflow-y-auto z-40 rounded-xl shadow-2xl
			p-4 m-6 bottom-0 left-0 bg-black bg-opacity-65"
		transition:fade={{ duration: 200 }}
	>
		{#if states.nodeInfo}
			{#if $selectedNodeStore}
				{#key $selectedNodeStore}
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
							{$selectedNodeStore.title}
						</div>
						<div>
							{$t('from')}
							<span class="text-white">{$selectedNodeStore.author}</span>
						</div>
						<div class="max-h-60 overflow-auto text-justify text-gray-300">
							{$selectedNodeStore.text}
						</div>
					</div>
				{/key}
			{:else}
				<div class="text-xl text-center font-semibold first-letter:capitalize">
					{$t('noNodeSelected')}
				</div>
			{/if}
		{:else if states.addNode}
			<form
				method="post"
				action="/sessions/{session.id}?/addNode"
				class="flex flex-col items-center gap-2 cursor-default p-2 z-10 w-full"
				onsubmit={(e) => {
					e.preventDefault();
					if (theForm) {
						validForm = theForm.checkValidity();
						if (validForm) {
							theForm.requestSubmit();
						}
					}
				}}
				use:enhance={() => {
					nProgress.start();
					return async ({ update, result }) => {
						await update({ reset: false });
						handleActionResult(result);
						nProgress.done();
					};
				}}
			>
				<label class="form-control w-full max-w-xs">
					<div class="label p-0">
						<span class="label-text text-inherit">{$t('messageTitle')}</span>
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
						<span class="label-text text-inherit">{$t('yourName')}</span>
					</div>
					<input
						name="author"
						type="text"
						bind:value={nodeAuthor}
						placeholder="Snoup"
						class="input input-sm input-accent text-primary-500 bg-gray-950 input-bordered w-full max-w-xs"
					/>
				</label>
				<label class="form-control w-full max-w-xs">
					<div class="label p-0">
						<span class="label-text text-inherit">{$t('side.yourSide')}</span>
					</div>
					<select
						name="side"
						class="select select-accent text-primary-500 bg-gray-950 select-sm select-bordered"
					>
						{#each sides as side}
							<option value={side.id}>{side.name}</option>
						{/each}
					</select>
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
				<input type="hidden" name="session" value={session.id} />
				<input type="hidden" name="parent" value={$selectedNodeStore?.id ?? null} />
				<button class="btn w-fit btn-accent btn-sm self-center" type="submit">{$t('form.submit')}</button>
			</form>
		{:else if states.admin}
			<div
				transition:slide={{
					duration: 200,
					easing: quintOut
				}}
				class="flex flex-col items-center gap-2 p-2 text-primary-500 z-10"
			>
				{@render formTemplate(events, 'addEvent', 'eventId', $t('sessions.addEvent'), true)}
				{@render formTemplate(ends, 'endSession', 'endId', $t('sessions.endSession'))}
			</div>
		{/if}
	</div>
{/if}
