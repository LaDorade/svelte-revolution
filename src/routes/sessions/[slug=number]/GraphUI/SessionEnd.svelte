<script lang="ts">
	import Overlay from './Overlay.svelte';
	import { getCurrentSessionCtx } from '$stores/session.svelte';

	const currentSession = getCurrentSessionCtx();
</script>

<Overlay>
	<div class="flex flex-col gap-4 p-2 z-10 max-w-80 text-sm">
		<h3
			class="text-lg font-semibold text-gray-50 first-letter:capitalize"
		>
			{currentSession.session.expand?.end?.title || 'Session Ended'}
		</h3>
		<div class="text-gray-200">
			{currentSession.session.expand?.end?.text}
		</div>
	</div>
</Overlay>