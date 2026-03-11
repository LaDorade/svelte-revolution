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
	import Overlay from './Overlay.svelte';
	import { getCurrentSessionCtx } from '$stores/session.svelte';

	import type { MainGraph } from '$stores/graph/Classes/MainGraph.svelte';
	import type { ActionResult } from '@sveltejs/kit';

	interface Props {
		graph: MainGraph | null;
		handleSubmit: (result: ActionResult) => void;
	}
	let {
		graph,
		handleSubmit,
	}: Props = $props();

	const currentSession = getCurrentSessionCtx();

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
	// 	&& (currentSession.admin.isAdmin ? userSideId : true)
	// 	&& (currentSession.admin.isAdmin ? pseudo.trim() : true)
	// );
</script>

<Overlay>
	<form
		in:fade={{ duration: 150 }}
		method="POST"
		enctype="multipart/form-data"
		action="/sessions/{currentSession.session.slug}?/addNode"
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
		{#if currentSession.admin.isAdmin}
			<Input
				required
				name="author"
				label={$t('home.yourName')}
				bind:value={currentSession.sessionProfile.pseudo}
				placeholder="Pseudo"
			/>
			<DropdownMenu.Root>
				<DropdownMenu.Trigger class="self-start" >
					<Button
						variant="ghost"
						class="self-start"
					>
						{#if currentSession.sessionProfile.choosedSideId}
							{$t('side.yourSide')} :
							<span class="italic">
								{currentSession.sides.find((side) => side.id === currentSession.sessionProfile.choosedSideId)?.name}
							</span>
						{:else}
							{$t('side.chooseSide')}
						{/if}
					</Button>
				</DropdownMenu.Trigger>
				<DropdownMenu.Content class="border-none gap-2 bg-gray-900" align="start">
					{#each currentSession.sides as side (side.id)}
						<DropdownMenu.Item
							class="cursor-pointer hover:bg-gray-800"
							onclick={() => (currentSession.sessionProfile.choosedSideId = side.id)}
						>
							{side.name}
						</DropdownMenu.Item>
					{/each}
				</DropdownMenu.Content>
			</DropdownMenu.Root>
			<input type="hidden" name="side" value={currentSession.sessionProfile.choosedSideId} />
		{:else}
			<Input
				required
				readonly
				name="author"
				label={$t('home.yourName')}
				value={currentSession.sessionProfile.pseudo}
			/>
			<Input
				required
				readonly
				label={$t('side.yourSide')}
				value={currentSession.sides.find((side) => side.id === currentSession.sessionProfile.choosedSideId)?.name}
			/>
			<input type="hidden" name="side" value={currentSession.sessionProfile.choosedSideId} />
		{/if}
		<input type="hidden" name="session" value={currentSession.session.id} />
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
		<Input
			name="audio"
			type="file"
			accept="audio/ogg, audio/mpeg, audio/wav, audio/mp3"
			label={$t('inSession.addAudio')}
		/>
		<Button variant="primary" type="submit" class="self-start mt-2">
			{$t('misc.submit')}
		</Button>
	</form>
</Overlay>