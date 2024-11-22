<script>
	import { ArrowUp } from 'lucide-svelte';
	import { onMount } from 'svelte';

	let showButton = $state(false);

	const handleScroll = () => {
		showButton = window.scrollY > 300;
	};

	const scrollToTop = () => {
		window.scrollTo({ top: 0, behavior: 'smooth' });
	};

	onMount(() => {
		window.addEventListener('scroll', handleScroll);
		return () => {
			window.removeEventListener('scroll', handleScroll);
		};
	});
</script>

<button
	class="fixed bottom-4 p-2 w-10 h-10 right-4 m-4 border border-white z-50 bg-black text-white rounded-full flex items-center justify-center cursor-pointer {showButton
		? ''
		: 'hidden'}"
	onclick={scrollToTop}
	aria-label="Back to top"
>
	<ArrowUp strokeWidth={1.5} color="white" />
</button>
