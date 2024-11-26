import { untrack } from 'svelte';

export function watch(callback: () => void, watched: unknown[]) {
	if (watched) {
		untrack(() => {
			callback();
		});
	}
}
