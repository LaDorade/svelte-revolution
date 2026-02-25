<script lang="ts">
	import { t } from 'svelte-i18n';
	import nProgress from 'nprogress';
	import toast from 'svelte-french-toast';
	import { pb } from '$lib/client/pocketbase';
	import { invalidateAll } from '$app/navigation';

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
		class="flex flex-col items-center self-center w-full gap-4 sm:w-1/2"
	>
		<div class="flex flex-col items-start w-full gap-4 text-black dark:text-white">
			<label class="flex items-center w-full gap-2 input input-bordered input-accent">
				{$t('login.username')} |
				<input
					type="text"
					class="grow"
					bind:value={username}
					placeholder="Snoup !"
					autocomplete="username"
					name="username"
				/>
			</label>
			<label class="flex items-center w-full gap-2 input input-bordered input-accent">
				{$t('login.password')} |
				<input
					type="password"
					bind:value={password}
					class="grow"
					placeholder="••••••••"
					autocomplete="current-password"
					name="password"
				/>
			</label>
			<div class="flex flex-row items-center justify-center w-full h-12">
				<button type="submit" class="p-4 font-bold w-fit btn btn-accent">{$t('login.login')}</button>
			</div>
		</div>
	</form>
</div>
