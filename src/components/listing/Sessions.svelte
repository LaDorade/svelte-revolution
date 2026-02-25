<script lang="ts">
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { t } from 'svelte-i18n';
	import { pb } from '$lib/client/pocketbase';
	import graphe1 from '$lib/assets/graphe1.png';

	import Tooltip from '$components/Tooltip.svelte';
	import { fade } from 'svelte/transition';
	import { resolve } from '$app/paths';
	import type { Session } from '$types/pocketBase/TableTypes';

	interface Props {
		sessions: Session[];
		admin?: boolean;
	}
	let { sessions, admin = false }: Props = $props();

	sessions = sessions?.sort((a) => (a.completed ? 1 : -1));

	function getSessionUrl(session: Session) {
		return `/sessions/${session.slug}?${admin ? 'admin=true' : ''}` as const;
	}

	function getSessionImage(session: Session) {
		return session.image ? pb.files.getURL(session, session.image) : graphe1;
	}

	// update sessions in realtime when a new session is created
	async function realtimeSessionUpdate() {
		await pb.collection('Session').subscribe('*', (data) => {
			const record = data.record;
			if (!sessions) {
				sessions = [data.record];
				return;
			}
			const index = sessions?.findIndex((session) => session.id === record.id);
			if (index !== -1) {
				sessions[index] = record;
			} else {
				sessions.push(record);
			}
		});
	}

	onMount(async () => {
		await realtimeSessionUpdate();
	});
</script>

<div class=" w-5/6 sm:w-4/5">
	{#if sessions?.length}
		<ul class="grid grid-flow-row lg:grid-cols-3 sm:grid-cols-2 gap-4 text-black">
			{#each sessions as session (session.id)}
				{@const completed = session.completed}
				{@const scenario = session.expand?.scenario}
				{@const imageUrl = getSessionImage(session)}
				<li
					animate:flip={{ duration: 300 }}
					class="w-full h-full flex relative flex-col items-center rounded-lg {completed
						? ' bg-amber-800'
						: 'bg-primary-600'}"
				>
					<div class=" w-full h-full">
						<Tooltip>
							<a
								tabindex="0"
								class="grid hover:z-20 w-full h-full grid-cols-[3fr_1fr] p-4 hover:scale-105 transition-all rounded-lg {completed
									? ' bg-amber-700'
									: 'bg-primary-500'}"
								href={resolve(getSessionUrl(session))}
							>
								<div>
									<h3 class="text-lg font-semibold text-ellipsis capitalize justify-self-start">
										{session.name}
									</h3>
									<div class="w-full">
										{$t('scenario.scenario')}:
										<span
											class="italic underline text-pretty text-ellipsis font-light cursor-default hover:underline"
										>{scenario?.title}</span
										>
									</div>
								</div>
								<div class="w-12 h-12 p-0 flex justify-center justify-self-end">
									<img
										class="rounded-lg p-0 h-12 w-12 object-cover"
										src={session.image ? imageUrl : graphe1}
										alt="session"
									/>
								</div>
							</a>
							{#snippet tooltip()}
								<div
									class="absolute h-fit w-full z-50 top-12 m-4 cursor-text"
									in:fade={{ duration: 100, delay: 400 }}
								>
									<div
										class="p-2 w-fit text-balance text-white rounded bg-gray-900 bg-opacity-90 flex flex-col gap-2"
									>
										<div class="text-lg text-start">
											{scenario?.title}
										</div>
										<div class=" text-sm text-gray-200 line-clamp-3">
											{scenario?.prologue}
										</div>
									</div>
								</div>
							{/snippet}
						</Tooltip>
					</div>

					<div class="w-full flex justify-between p-1 pl-2 bg-inherit rounded-b-lg">
						{#if session.expand?.author}
							<div>
								{$t('scenario.author')} : {session.expand?.author?.username}
							</div>
						{/if}
						<div>
							{new Date(session.created).toISOString().split('T')[0]}
						</div>
					</div>
				</li>
			{/each}
		</ul>
	{:else}
		<div class="text-center">
			{$t('sessions.noSessions')}
		</div>
	{/if}
</div>
