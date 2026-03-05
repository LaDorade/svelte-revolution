<script lang="ts">
	import { t } from 'svelte-i18n';
	import nProgress from 'nprogress';
	import toast from 'svelte-french-toast';
	import { pb } from '$lib/client/pocketbase';
	import { invalidateAll } from '$app/navigation';
	import Input from '$components/form/Input.svelte';
	import Button from '$components/Button.svelte';

	let username = $state('');
	let password = $state('');
</script>

<div class="flex flex-col w-full gap-4 py-4 text-center">
	<h1 class="text-4xl font-thin text-center text-white first-letter:capitalize">{$t('admin.administration')}</h1>
	<form
		onsubmit={async (e) => {
			e.preventDefault();
			nProgress.start();
			try {
				await pb.collection('Users').authWithPassword(username, password);
				if (pb.authStore.isValid) {
					toast.success('Logged in');
					invalidateAll(); // * Important to avoid infinite loop
				} else {
					toast.error('Invalid credentials', { position: 'bottom-center' });
				}
			} catch {
				toast.error('Invalid credentials', { position: 'bottom-center' });
			}
			nProgress.done();
		}}
		method="post"
		class="self-center flex flex-col w-full gap-4 sm:w-1/2"
	>
		<Input
			{@attach (node) => node.focus()}
			label={$t('login.username')}
			bind:value={username}
			placeholder="Snoup !"
			type="text"
			autocomplete="username"
			name="username"
		/>
		<Input
			label={$t('login.password')}
			bind:value={password}
			placeholder="••••••••"
			type="password"
			autocomplete="current-password"
			name="password"
		/>
		<Button
			variant="primary"
			type="submit"
			class="w-fit self-end"
		>
			{$t('login.login')}
		</Button>
	</form>
</div>
