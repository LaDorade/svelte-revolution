<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import Button from '$components/Button.svelte';
	import { Pause, Play, Volume1, Volume2, VolumeOff } from 'lucide-svelte';
	import { onMount } from "svelte";

	interface Props {
		audioPath: string;
	}
	let {
		audioPath
	}: Props = $props();

	let time = $state(0);
	let duration = $state(0);
	let paused = $state(true);
	let volume = $state(1);

	function onVolumeChange() {
	  localStorage.setItem("audioVolume", String(volume));
	}
	onMount(() => {
	  const audioVolume = localStorage.getItem("audioVolume");
	  if (!audioVolume) return;

	  volume = Number(audioVolume);
	});
</script>

<div class="flex items-center gap-2 w-full border border-gray-800 rounded-lg p-2">
	{#if paused}
		<Button class="p-2 rounded-full" variant="secondary" onclick={() => paused = false}>
			<Play strokeWidth="1.5" class="w-4 h-4" />
		</Button>
	{:else}
		<Button class="p-2 rounded-full" variant="secondary" onclick={() => paused = true}>
			<Pause strokeWidth="1.5" class="w-4 h-4" />
		</Button>
	{/if}
	<input
		type="range"
		min="0"
		max={duration}
		step="0.01"
		bind:value={time}
		class={['appearance-none h-1 w-full rounded-full bg-gray-700 cursor-pointer [&::-webkit-slider-thumb]:appearance-none',
			'[&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full',
			'[&::-webkit-slider-thumb]:bg-primary-500 [&::-webkit-slider-thumb]:cursor-pointer',
		]}
	/>
	<span class="text-xs text-gray-400 font-mono">
		{Math.floor(time / 60)}:{String(Math.floor(time % 60)).padStart(2, '0')}
	</span>
	<DropdownMenu.Root>
		<DropdownMenu.Trigger class="p-2 cursor-pointer">
			{#if volume === 0}
				<VolumeOff strokeWidth="1.5" class="w-4 h-4 text-gray-500" />
			{:else if volume < 0.5}
				<Volume1 strokeWidth="1.5" class="w-4 h-4" />
			{:else}
				<Volume2 strokeWidth="1.5" class="w-4 h-4" />
			{/if}
		</DropdownMenu.Trigger>
		<DropdownMenu.Content class="bg-gray-800 border-none w-fit min-w-0 p-2 rounded-md">
			<input
				type="range"
				min="0"
				max="1"
				step="0.01"
				bind:value={volume}
				onchange={onVolumeChange}
				class={[
					'appearance-none w-1 h-20 rounded-full bg-gray-700 cursor-pointer [&::-webkit-slider-thumb]:appearance-none',
					'[&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full',
					'[&::-webkit-slider-thumb]:bg-primary-500 [&::-webkit-slider-thumb]:cursor-pointer',
					'[direction:rtl] [writing-mode:vertical-lr]',
				]}
			/>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
	<audio
		bind:currentTime={time}
		bind:duration
		bind:paused
		bind:volume
		onended={() => {
			time = 0;
			paused = true;
		}}
		class="w-full rounded-lg"
		src={audioPath}
	></audio>
</div>
