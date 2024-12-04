<script lang="ts">
	import { onMount } from 'svelte';
	import { quintOut } from 'svelte/easing';
	import { fade, scale } from 'svelte/transition';
	import { replaceState } from '$app/navigation';
	import ExampleGraph from '$components/graph/ExampleGraph.svelte';
	import { typewriter } from '$lib/animations';
	import { t, locale } from 'svelte-i18n';
	import { homeStore } from '$stores/graph/home/index.svelte.js';
	import { titleStore } from '$stores/titles/index.svelte';
	import toast from 'svelte-french-toast';

	import graph1 from '$lib/assets/graphe1.png';
	import Sessions from '$components/listing/Sessions.svelte';

	let visible = $state(false);
	let userMessage = $state('');

	let { data } = $props();

	// Hack to force the graph to reload when the locale changes
	let reloadGraph = $derived(String(homeStore.nodes.length) + String($locale));

	function submitUserMessage(e: SubmitEvent) {
		e.preventDefault();
		if (userMessage) {
			const id = homeStore.nodes.length + 1;
			const node = homeStore.addNode({
				id,
				title: $t('home.yourMessage'),
				text: userMessage
			});
			homeStore.addLink({ source: Number(id), target: Number(homeStore.selectedNode?.id) ?? 3 });
			userMessage = '';
			homeStore.selectedNode = node;
		} else {
			toast.error($t('home.emptyMessage'));
		}
	}

	onMount(() => {
		visible = true;

		const url = new URL(window.location.href);
		const newUrl = url.toString().split('#');
		if (newUrl[1]) {
			replaceState(newUrl[0], {});
		}

		titleStore.setNavTitle('Babel Revolution');
	});
</script>

<div class="flex flex-col items-center w-full gap-12 px-4">
	<section class="flex flex-col items-center w-full gap-6 p-8 pb-0 md:w-2/3">
		<h1 class="pb-0 text-nowrap max-md:text-4xl">
			{#if visible}
				<span in:typewriter|global={{ text: 'BⱯBEL RËVOLUㅏION' }} class="text-white"></span>
				<span class="blinking-underscore">_</span>
			{:else}
				<span class="invisible">BABEL REVOLUTION</span>
			{/if}
		</h1>
		<div class="text-lg text-pretty text-gray-100">
			{$t('home.intro')}
			<p class="text-white">
				{$t('home.introHighlight')}
				<span class="text-primary-500 text-nowrap">{$t('home.introHyperHighlight')}</span>
			</p>
		</div>
		<div id="intro" class="grid grid-cols-2 grid-rows-2 gap-4">
			<a class="btn dark:bg-white dark:text-black hover:bg-gray-300" href="#intro">{$t('home.discoverBabel')}</a>
			<a class="text-white bg-gray-800 btn w-fit hover:bg-gray-900" href="/sessions">{$t('home.joinSession')}</a>
			<a class="btn col-span-2 bg-primary-500 text-black border-none" href="#animer"
				>{$t('home.animateYourSession')}</a
			>
		</div>
	</section>
	<div
		class="flex flex-col-reverse items-center w-full gap-0 px-12 lg:h-80 md:px-40 xl:px-64 lg:flex-row-reverse md:justify-center"
	>
		<div
			in:scale={{
				delay: 50,
				duration: 400,
				easing: quintOut
			}}
			class="flex flex-col w-full h-full gap-4 text-balance item md:py-12"
		>
			{#key homeStore.selectedNode}
				<div
					in:fade={{
						duration: 400
					}}
					class="flex flex-col w-full text-gray-200"
				>
					<div class="text-xl font-semibold first-letter:capitalize text-gray-100">
						{$t(homeStore.selectedNode?.title ?? 'oupsi')}
					</div>
					<div class="">{$t(homeStore.selectedNode?.text ?? 'oupsi')}</div>
					{#if homeStore.selectedNode?.id === 3}
						<form class="flex justify-between mt-2 items-center" onsubmit={submitUserMessage}>
							<input
								type="text"
								bind:value={userMessage}
								placeholder={$t('home.writeMessage')}
								class="max-w-xs input border-primary-500 appearance-none bg-black"
							/>
							<button type="submit" class=" btn btn-accent">{$t('home.send')}</button>
						</form>
					{:else if homeStore.selectedNode?.id === 5}
						<div class="mt-2 chat chat-end">
							<div class="rounded-full chat-image avatar ring-primary-500 ring-1">
								<div class="w-10 rounded-full">
									<img alt="avatar" src={graph1} />
								</div>
							</div>
							<div class="mr-2 text-black chat-bubble bg-primary-500">
								{$t('home.tryDragGraph')}
							</div>
						</div>
					{/if}
				</div>
			{/key}
		</div>
		<div class="w-full text-left sm:flex sm:justify-center">
			{#key reloadGraph}
				<ExampleGraph />
			{/key}
		</div>
	</div>
	<div class="flex flex-col w-full text-gray-50 gap-4 items-center">
		<h2>Sessions Ouvertes</h2>
		<Sessions sessions={data.sessions?.filter((session) => !session.completed)} />
		<h2>Sessions Terminées</h2>
		<Sessions sessions={data.sessions?.filter((session) => session.completed)} />
	</div>
	<div class="flex flex-col w-full text-gray-200 gap-4 items-cente">
		<h2 id="animer" class="text-3xl text-gray-100 font-bold">Animer votre Session</h2>
		<div class="text-pretty p-8 bg-black bg-opacity-30 mx-24 rounded">
			{$t('home.animateSession')}
		</div>
	</div>
	<footer class=" text-gray-300 backdrop-blur-[2px] -mx-4 p-4 border-primary-500 border-t">
		<div class="text-center flex items-center flex-col gap-2 antialiased">
			<svg
				width="50"
				height="50"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				fill-rule="evenodd"
				clip-rule="evenodd"
				class="inline-block fill-current text-primary-500"
			>
				<path
					d="M22.672 15.226l-2.432.811.841 2.515c.33 1.019-.209 2.127-1.23 2.456-1.15.325-2.148-.321-2.463-1.226l-.84-2.518-5.013 1.677.84 2.517c.391 1.203-.434 2.542-1.831 2.542-.88 0-1.601-.564-1.86-1.314l-.842-2.516-2.431.809c-1.135.328-2.145-.317-2.463-1.229-.329-1.018.211-2.127 1.231-2.456l2.432-.809-1.621-4.823-2.432.808c-1.355.384-2.558-.59-2.558-1.839 0-.817.509-1.582 1.327-1.846l2.433-.809-.842-2.515c-.33-1.02.211-2.129 1.232-2.458 1.02-.329 2.13.209 2.461 1.229l.842 2.515 5.011-1.677-.839-2.517c-.403-1.238.484-2.553 1.843-2.553.819 0 1.585.509 1.85 1.326l.841 2.517 2.431-.81c1.02-.33 2.131.211 2.461 1.229.332 1.018-.21 2.126-1.23 2.456l-2.433.809 1.622 4.823 2.433-.809c1.242-.401 2.557.484 2.557 1.838 0 .819-.51 1.583-1.328 1.847m-8.992-6.428l-5.01 1.675 1.619 4.828 5.011-1.674-1.62-4.829z"
				></path>
			</svg>
			<p class="text-xl font-semibold">Babel Révolution | UTC</p>
			<div class=" bg-black flex flex-col gap-2 bg-opacity-20 text-justify rounded-lg p-2">
				<blockquote>
					« {$t('home.footer.citation')} »
					<br />
					<div class=" italic font-semibold">Klemperer, LTI, la langue du Troisième Reich, 1947</div>
				</blockquote>
				{$t('home.footer.mainText')}
			</div>
			<div>
				<div class="text-lg font-semibold">{$t('home.footer.credits')}</div>
				<div class="text-primary-500">Serge Bouchardon, Isabelle Cros, Erika Fülöp, Simon Renaud.</div>
			</div>
			<div>
				<div class="text-lg font-semibold">{$t('home.footer.devAndDesign')}</div>
				<div class="text-primary-500 text-balance">
					Mathis Jung, Eileen Lorenzo, Eva Guignabodet, Florestan Biaux, Benoît Chevillon, Lucas D'Aquaro,
					Solène Desvaux de Marigny, Ismaïl Kadiri, Mathilde Lange, Claire Malgonne, Gabrielle Van de Vijver
				</div>
			</div>
			<div>
				<p class="text-lg font-semibold">{$t('home.footer.techUsed')}</p>
				<p class="text-primary-500">Svelte, SvelteKit, TailwindCSS, PocketBase, Lucide Icons, Docker</p>
			</div>
			<p class="text-sm">{new Date().getFullYear()}</p>
		</div>
	</footer>
</div>

<style>
	.blinking-underscore {
		animation: blink 1s step-start infinite 2s;
	}

	@keyframes blink {
		50% {
			opacity: 0;
		}
	}
</style>
