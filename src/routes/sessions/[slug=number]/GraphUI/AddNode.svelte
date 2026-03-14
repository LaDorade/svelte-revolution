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
		class="flex flex-col gap-2 text-sm min-w-80"
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
		<h3 class="text-gray-50 px-4 py-2 border-b border-gray-500 text-lg font-semibold">
			{$t('inSession.contribute')}
		</h3>
		<Input
			required
			name="title"
			label={$t('home.messageTitle')}
			placeholder="Youhouhou"
			bind:value={nodeTitle}
		/>
		<Textarea
			required
			name="text"
			label={$t('home.yourMessage')}
			placeholder="Ton message"
			bind:value={nodeText}
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
				<DropdownMenu.Trigger class="self-start px-4 py-2">
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
		{/if}
		<Input
			readonly
			label={graph?.selectedNode ? $t('inSession.replyingTo') : $t('inSession.noNodeSelected')}
			value={graph?.selectedNode?.title ?? $t('inSession.noNodeSelected')}
		/>
		{#if currentSession.session.useAudio}
			<Input
				name="audio"
				type="file"
				accept="audio/ogg, audio/mpeg, audio/wav, audio/mp3"
				label={$t('inSession.addAudio')}
			/>
		{/if}
		<div class="px-4 py-2">
			<Button variant="primary" type="submit" class="self-start">
				{$t('form.send')}
			</Button>
		</div>
		<input readonly required type="hidden" name="parent"  value={graph?.selectedNode?.id}/>
		<input readonly required type="hidden" name="side"    value={currentSession.sessionProfile.choosedSideId} />
		<input readonly required type="hidden" name="session" value={currentSession.session.id} />
	</form>
</Overlay>