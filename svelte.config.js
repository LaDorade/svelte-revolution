import adapterAuto from '@sveltejs/adapter-auto';
import adapterNode from '@sveltejs/adapter-node';
import 'dotenv/config';

const adapterType = process.env.ADAPTER || 'auto';

const adapter = () => {
	switch (adapterType) {
		case 'node':
			return adapterNode();
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
		adapter: adapter(),
		alias: {
			$components: './src/components',
			$stores: './src/stores',
			$types: './src/types'
		}
	}
};

export default config;
