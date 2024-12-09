<script lang="ts">
	import { page } from '$app/stores';
	import { t } from 'svelte-i18n';
</script>

<div class="h-screen divide-gray-400">
	<div class="h-full flex flex-col justify-center items-center">
		<div class="flex items-center justify-center divide-x">
			<div class="text-6xl font-light p-4">{$page.error?.status || $page.status || '404'}</div>
			<div class="text-2xl font-thin p-4">
				{$page.error?.message}
			</div>
		</div>
		<a class="btn btn-accent" href="/">{$t('errors.returnInSafePlace')}</a>
	</div>
</div>
