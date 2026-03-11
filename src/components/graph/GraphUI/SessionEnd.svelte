<script lang="ts">
	import Overlay from './Overlay.svelte';

	import type { Session } from '$types/pocketBase/TableTypes';

	interface Props {
		session: Session;
	}
	let { session }: Props = $props();
</script>

<Overlay>
	<div
		class="flex flex-col gap-4 p-2 z-10 max-w-80 text-sm"
	>
		<h3
			class="text-lg font-semibold text-gray-50 first-letter:capitalize"
		>
			{session.expand?.end?.title}
		</h3>
		<div class="text-gray-200">
			{session.expand?.end?.text}
		</div>
	</div>
</Overlay>