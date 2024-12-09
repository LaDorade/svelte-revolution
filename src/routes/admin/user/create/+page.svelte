<script lang="ts">
	import { enhance } from '$app/forms';
	import { t } from 'svelte-i18n';
	import toast from 'svelte-french-toast';
	import nProgress from 'nprogress';
	import type { ActionData } from './$types';

	interface Props {
		form: ActionData;
	}
	let { form }: Props = $props();

	let theForm: HTMLFormElement;
	let validForm = $state(false);

	$effect(() => {
		if (form?.success) {
			toast.success($t('admin.user.creationSuccess'), {
				duration: 5000,
				position: 'bottom-center'
			});
		}
		if (form?.error) {
			toast.error(form.error, { duration: 5000, position: 'bottom-center' });
		}
	});
</script>

<div class="flex flex-col items-center">
	<h1 class="p-4 text-3xl font-bold">{$t('admin.user.createUser')}</h1>
	<form
		action="?/createUser"
		method="POST"
		bind:this={theForm}
		oninput={() => (validForm = theForm?.checkValidity())}
		use:enhance={() => {
			nProgress.start();
			return async ({ update }) => {
				await update();
				nProgress.done();
			};
		}}
		class="flex flex-col gap-4 p-4 text-center border-t shadow-md"
	>
		<div class="flex flex-col gap-4">
			<div class="w-full">
				<label for="username" class="text-lg font-thin">{$t('login.username')}</label>
				<input
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
			class="self-center px-4 py-2 text-lg text-black transition-all ease-linear bg-white rounded disabled:cursor-not-allowed disabled:opacity-50"
		>
			{$t('admin.user.createUser')}
		</button>
	</form>
</div>
