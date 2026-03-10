<script lang="ts">
	import { applyAction, enhance } from '$app/forms';
	import nProgress from 'nprogress';
	import toast from 'svelte-french-toast';
	import { t } from 'svelte-i18n';
	import { fade } from 'svelte/transition';
	import Textarea from '$components/form/Area.svelte';
	import Input from '$components/form/Input.svelte';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import Button from '$components/Button.svelte';

	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { ActionResult } from '@sveltejs/kit';
	import type { Session, Side } from '$types/pocketBase/TableTypes';

	interface Props {
		graph: MainGraph | null;
		handleSubmit: (result: ActionResult) => void;
		admin: boolean;
		userSideId: string | null;
		sides: Side[];
		pseudo: string | null;
		session: Session;
	}
	let {
		graph,
		handleSubmit,
		admin,
		userSideId,
		sides,
		pseudo,
		session
	}: Props = $props();

	let nodeTitle = $state('');
	let nodeText = $state('');

	async function submit({ result }: { result: ActionResult }) {
		try {
			applyAction(result);
			handleSubmit(result);
		} catch (e) {
			console.error(e);
			toast.error($t('error.unknownError'), {
				duration: 3000,
				position: 'bottom-center',
			});
		}
		finally {
			nProgress.done();
		}
	}

// ? Its better to let the user get an error because right now its not explicit why the button is disabled
	// let valid = $derived(
	// 	graph.selectedNode && nodeTitle.trim() && nodeText.trim()
	// 	&& (admin ? userSideId : true)
	// 	&& (admin ? pseudo.trim() : true)
	// );
</script>

<form
	in:fade={{ duration: 200 }}
	method="POST"
	action="/sessions/{session.slug}?/addNode"
	class="flex flex-col gap-4 cursor-default z-10 p-2 text-sm"
	onsubmit={(e) => {
		e.preventDefault();
	}}
	use:enhance={() => {
		nProgress.start();
		if (!graph?.selectedNode) {
			toast.error($t('inSession.noNodeSelected'), {
				duration: 3000,
				position: 'bottom-center',
			});
			nProgress.done();
			return;
		}
		return submit;
	}}
>
	<h3 class="text-gray-50 py-2 text-lg font-semibold">
		{$t('inSession.contribute')}
	</h3>
	<Input
		required
		name="title"
		label={$t('home.messageTitle')}
		bind:value={nodeTitle}
		placeholder="Youhouhou"
	/>
	<Textarea
		required
		name="text"
		label={$t('home.yourMessage')}
		bind:value={nodeText}
		placeholder="Ton message"
	/>
	{#if admin}
		<Input
			required
			name="author"
			label={$t('home.yourName')}
			bind:value={pseudo}
			placeholder="Pseudo"
		/>
		<DropdownMenu.Root>
			<DropdownMenu.Trigger class="self-start" >
				<Button
					variant="secondary"
					class="self-start"
				>
					{#if userSideId}
						{$t('side.yourSide')} :
						<span class="italic">
							{sides.find((side) => side.id === userSideId)?.name}
						</span>
					{:else}
						{$t('side.chooseSide')}
					{/if}
				</Button>
			</DropdownMenu.Trigger>
			<DropdownMenu.Content class="border-none gap-2 bg-gray-900" align="start">
				{#each sides as side (side.id)}
					<DropdownMenu.Item
						class="cursor-pointer hover:bg-gray-800"
						onclick={() => (userSideId = side.id)}
					>
						{side.name}
					</DropdownMenu.Item>
				{/each}
			</DropdownMenu.Content>
		</DropdownMenu.Root>
		<input type="hidden" name="side" value={userSideId} />
	{:else}
		<Input
			required
			readonly
			name="author"
			label={$t('home.yourName')}
			value={pseudo}
		/>
		<Input
			required
			readonly
			name="side"
			label={$t('side.yourSide')}
			value={sides.find((side) => side.id === userSideId)?.name}
		/>
		<input type="hidden" name="side" value={userSideId} />
	{/if}
	<input type="hidden" name="session" value={session.id} />
	<Input
		readonly
		label={graph?.selectedNode ? $t('inSession.replyingTo') : $t('inSession.noNodeSelected')}
		value={graph?.selectedNode?.title ?? $t('inSession.noNodeSelected')}
	/>
	<input
		readonly
		required
		type="hidden"
		name="parent"
		value={graph?.selectedNode?.id ?? null}
	/>
	<Button variant="primary" type="submit" class="self-start mt-2">
		{$t('misc.submit')}
	</Button>
</form>