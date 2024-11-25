<script lang="ts">
	import toast_, { type Toast } from 'svelte-french-toast';
	import type { GraphNode } from '$types/pocketBase/TableTypes';
	import { mainGraphStore } from '$stores/graph/main/store.svelte';
	import { t } from 'svelte-i18n';

	type MyToast = Toast & { props: { record: GraphNode; author: string } };

	interface Props {
		toast: MyToast;
	}

	let { toast }: Props = $props();
</script>

<span class="flex flex-col items-center">
	<button onclick={() => (mainGraphStore.selectedNode = toast.props.record)}
		>{$t('toast.newMessageBy') + toast.props.author}</button
	>
	<button onclick={() => toast_.dismiss(toast.id)}>Dismiss</button>
</span>
