<script lang="ts">
	import { t } from 'svelte-i18n';
	import toast from 'svelte-french-toast';
	import nProgress from 'nprogress';
	import { pb } from '$lib/client/pocketbase';
	import type { ClientResponseError } from 'pocketbase';

	let formData = $state({
		username: '',
		password: ''
	});

	const validForm = $derived.by(() => {
		return formData.username.length >= 3 && formData.password.length >= 3;
	});

	const createUser = async () => {
		nProgress.start();
		const { username, password } = formData;

		try {
			const user = await pb.collection('Users').create({
				username,
				password,
				passwordConfirm: password,
				name: username,
				role: 'admin'
			});
			return {
				status: 201,
				success: true,
				user
			};
		} catch (err) {
			const error = err as ClientResponseError;
			console.error(error);
			toast.error(error.message);
		}
		nProgress.done();
	};
</script>

<div class="flex flex-col items-center justify-center w-full h-full">
	<div class="flex flex-col items-center p-4 shadow-xl rounded-xl bg-black/30">
		<h1 class="p-4 text-3xl font-bold">{$t('admin.user.createUser')}</h1>
		<div class="flex flex-col gap-4 p-4 text-center border-t">
			<div class="flex flex-col gap-4">
				<div class="w-full">
					<label for="username" class="text-lg font-thin">{$t('login.username')}</label>
					<input
						bind:value={formData.username}
						pattern={'[a-zA-Z0-9]{3,}'}
						required
						name="username"
						placeholder="Super Snoup"
						class="w-full p-4 border-b placeholder:font-thin placeholder:italic focus:border-white"
					/>
				</div>
				<div class="w-full">
					<label for="password" class="text-lg font-thin">{$t('login.password')}</label>
					<input
						bind:value={formData.password}
						required
						placeholder="Snoup mange des pommes tous les matins"
						type="password"
						name="password"
						class="w-full p-4 border-b placeholder:font-thin placeholder:italic focus:border-white"
					/>
				</div>
			</div>
			<button
				type="submit"
				disabled={!validForm}
				onclick={createUser}
				class="self-center px-4 py-2 text-lg text-black transition-all ease-linear bg-white rounded disabled:cursor-not-allowed disabled:opacity-50"
			>
				{$t('admin.user.createUser')}
			</button>
		</div>
	</div>
</div>
