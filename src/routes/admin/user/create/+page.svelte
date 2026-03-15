<script lang="ts">
	import { t } from 'svelte-i18n';
	import toast from 'svelte-french-toast';
	import nProgress from 'nprogress';
	import { pb } from '$lib/client/pocketbase';
	import Input from '$components/form/Input.svelte';
	import Button from '$components/Button.svelte';
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

<div class="flex flex-col items-center justify-center text-gray-100">
	<div class="w-fit p-4 flex flex-col items-center shadow-xl rounded-xl bg-black/30">
		<h1 class="py-4 text-3xl font-semibold">{$t('admin.user.createUser')}</h1>
		<div class="w-full min-w-80 flex flex-col gap-4 p-4 text-center border-t">
			<Input
				labelClass="w-full"
				name="username"
				bind:value={formData.username}
				pattern={'[a-zA-Z0-9]{3,}'}
				required
				label={$t('login.username')}
				placeholder="Super Snoup"
			/>
			<Input
				labelClass="w-full"
				name="password"
				bind:value={formData.password}
				required
				type="password"
				label={$t('login.password')}
				placeholder="Snoup mange des pommes tous les matins"
			/>
			<Button
				type="submit"
				disabled={!validForm}
				onclick={createUser}
				variant="primary"
			>
				{$t('admin.user.createUser')}
			</Button>
		</div>
	</div>
</div>
