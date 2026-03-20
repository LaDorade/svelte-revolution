import adapterNode from '@sveltejs/adapter-node';
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local', override: true });
dotenv.config();

const checkOrigin = process.env.CSRF_CHECK_ORIGIN === 'true';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapterNode(),
		alias: {
			$components: './src/components',
			$stores: './src/stores',
			$types: './src/types'
		},
		csrf: {
			trustedOrigins: checkOrigin ? [
				'https://new.babel-revolution.fr',
				'https://svelte-revolution.vercel.app',
				'http://localhost:5173'
			] : []
		},
	},
	vitePlugin: {
		inspector: {
			showToggleButton: 'always',
			toggleButtonPos: 'bottom-right',
		}
	},
	vitePlugin: {
		inspector: {
			showToggleButton: 'always',
			toggleButtonPos: 'bottom-right'
		}
	}
};

export default config;
