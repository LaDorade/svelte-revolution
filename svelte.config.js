import adapterAuto from '@sveltejs/adapter-auto';
import adapterNode from '@sveltejs/adapter-node';
import 'dotenv/config';

const adapterType = process.env.ADAPTER || 'auto';
const checkOrigin = process.env.CSRF_CHECK_ORIGIN === 'true';

const adapter = () => {
	switch (adapterType) {
	case 'node':
		return adapterNode();
	case 'auto':
	default:
		return adapterAuto();
	}
};

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter(),
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
