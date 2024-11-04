import adapterAuto from '@sveltejs/adapter-auto';
import adapterBun from 'svelte-adapter-bun';
import adapterNode from '@sveltejs/adapter-node';
import 'dotenv/config';

const adapterType = process.env.ADAPTER || 'auto';

const adapter = () => {
	switch (adapterType) {
		case 'node':
			return adapterNode();
		case 'bun':
			return adapterBun();
		case 'auto':
		default:
			return adapterAuto();
	}
};

const config = {
	compilerOptions: {
		runes: true
	},
	vitePlugin: {
		dynamicCompileOptions({ filename }) {
			if (filename.includes('node_modules')) {
				return { runes: undefined };
			}
		}
	},
	kit: {
		adapter: adapter(), // See https://kit.svelte.dev/docs/adapters
		alias: {
			$components: './src/components',
			$stores: './src/stores',
			$types: './src/types'
		}
	}
};

export default config;
