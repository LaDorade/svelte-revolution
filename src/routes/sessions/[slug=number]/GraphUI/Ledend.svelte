<script lang="ts">
	import { getCurrentSessionCtx } from '$stores/session.svelte';

	const currentSession = getCurrentSessionCtx();
</script>

<!-- Sides legend -->
<div
	class="fixed max-h-3/4 overflow-y-auto z-40 rounded-xl shadow-2xl p-4 bottom-0 left-0 bg-black bg-opacity-30"
>
	{#each currentSession.sides as side (side.id)}
		<div class="text-white flex items-center">
			<svg class="w-4 h-4 mr-1" viewBox="-12 -12 24 24">
				<path d={side.icon} fill="white" />
			</svg>
			{side.name}
		</div>
	{/each}
</div>