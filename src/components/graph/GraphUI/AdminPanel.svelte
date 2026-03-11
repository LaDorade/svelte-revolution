<script lang="ts">
	import { viewportStore } from '$stores/ui/index.svelte';
	import { t } from 'svelte-i18n';
	import Overlay from './Overlay.svelte';
	import { enhance } from '$app/forms';
	import nProgress from 'nprogress';
	import Checkbox from '$components/form/Checkbox.svelte';
	import Button from '$components/Button.svelte';
	import { ChevronDown } from 'lucide-svelte';

	import type { End, GraphEvent, Session } from '$types/pocketBase/TableTypes';
	import type { ActionResult } from '@sveltejs/kit';
	import type { MyPocketBase } from '$types/pocketBase';

	interface Props {
		pb: MyPocketBase;
		events: GraphEvent[];
		ends: End[];
		handleSubmit: (result: ActionResult) => void;
		session: Session;
	}
	let {
		pb,
		events,
		ends,
		handleSubmit,
		session
	}: Props = $props();
	
	function storePanelInLocalStorage() {
		localStorage.setItem(
			'seeDebugPanel',
			viewportStore.seeDebugPanel.toString(),
		);
	}

	let event = $state('');
	let endSession = $state('');

</script>

<Overlay>
	<div
		class="flex flex-col gap-4 p-2 text-primary-500 z-10 text-sm"
	>
		<div class="text-lg font-semibold text-gray-50 first-letter:capitalize">
			{$t('admin.controlPanel')}
		</div>
		<Checkbox
			label={$t('admin.debugPanel')}
			type="checkbox"
			name="seeDebugPane"
			id="debugPaneCheck"
			onchange={storePanelInLocalStorage}
			bind:checked={viewportStore.seeDebugPanel}
		/>
		<form
			method="POST"
			action="/sessions/{session.id}?/addEvent"
			onsubmit={(e) => {
				e.preventDefault();
			}}
			use:enhance={() => {
				nProgress.start();
				return async ({ result }) => {
					handleSubmit(result);
				};
			}}
			class="flex flex-col gap-2 text-gray-50 w-full"
		>
			<label class="flex items-center justify-between border-b border-gray-500 py-1 gap-2">
				<select bind:value={event} name="eventId" id="eventId" class="appearance-none grow cursor-pointer focus:outline-none">
					<option value="" class="bg-black text-gray-50 hover:bg-gray-900 appearance-none cursor-pointer" selected>
						{$t('admin.event.triggerEvent')}
					</option>
					{#each events as eve (eve.id)}
						<option class="bg-black text-gray-50 hover:bg-gray-900 appearance-none cursor-pointer" value={eve.id}>{eve.title}</option>
					{/each}
				</select>
				<ChevronDown
					class="w-4 h-4"
				/>
			</label>
			<input type="hidden" name="session" value={session.id} />
			<input
				type="hidden"
				name="pb_cookie"
				value={pb.authStore.exportToCookie()}
			/>
			<Button
				disabled={!event}
				variant="ghost"
				type="submit"
			>
				{$t('admin.event.triggerEvent')}
			</Button>
		</form>
		<form
			method="POST"
			action="/sessions/{session.id}?/endSession"
			onsubmit={(e) => {
				e.preventDefault();
			}}
			use:enhance={() => {
				nProgress.start();
				return async ({ result }) => {
					handleSubmit(result);
				};
			}}
			class="flex flex-col gap-2 text-gray-50 w-full"
		>
			<label class="flex items-center justify-between border-b border-gray-500 py-1 gap-2">
				<select bind:value={endSession} name="endId" id="endId" class="appearance-none grow cursor-pointer focus:outline-none">
					<option value="" class="bg-black text-gray-50 hover:bg-gray-900 appearance-none cursor-pointer" selected>
						{$t('admin.session.endSession')}
					</option>
					{#each ends as end (end.id)}
						<option class="bg-black text-gray-50 hover:bg-gray-900 appearance-none cursor-pointer" value={end.id}>{end.title}</option>
					{/each}
				</select>
				<ChevronDown
					class="w-4 h-4"
				/>
			</label>
			<input type="hidden" name="session" value={session.id} />
			<input
				type="hidden"
				name="pb_cookie"
				value={pb.authStore.exportToCookie()}
			/>
			<Button
				disabled={!endSession}
				variant="ghost"
				type="submit"
			>
				{$t('admin.session.endSession')}
			</Button>
		</form>
	</div>
</Overlay>