const cssSidePrefix = 'side-';

const graphColors = {
	nodes: {
		// hex colors or color names
		sides: '#9ef2bd',
		selected: '#ffed7a',
		start: '#ff7a7a',
		event: '#ff7a7a',
		connected: '#FF00FF',
		hidden: 'black'
	},
	links: {
		default: 'white',
		hover: '#FF0000',
		toHide: 'gray'
	}
};

// ne pas exporter
const icons = {
	circle: 'M12 0a12 12 0 1 0 0 24a12 12 0 1 0 0 -24z',
	square: 'M-12 -12h24v24h-24z',
	triangle: 'M0 -12L12 12H-12z',
	hexagon: 'M12 2.31l9.8 5.66a2 2 0 0 1 1 1.73v11.32a2 2 0 0 1-1 1.73l-9.8 5.66a2 2 0 0 1-2 0l-9.8-5.66a2 2 0 0 1-1-1.73V9.7a2 2 0 0 1 1-1.73l9.8-5.66a2 2 0 0 1 2 0z',
	diamond: 'M0 -12L12 0L0 12L-12 0z'
}

const graphIcons = [icons.square, icons.triangle, icons.hexagon, icons.diamond, icons.circle];
const graphIconEvent = icons.circle;

const labels = {
	default: 'white',
	hidden: 'transparent'
};

const strokeDashArray = {
	default: '5, 15',
	hover: 'none'
};

const nodeRadius = {
	default: 20,
	selected: 25,
	start: 30,
	event: 25
};

const nodeScale = {
	default: {
		default: 1.2,
		selected: 1.6
	},
	start: {
		default: 2.5,
		selected: 2.9
	},
	event: {
		default: 2,
		selected: 2.4
	}
};

export default {
	graphColors,
	graphIcons,
	graphIconEvent,
	cssSidePrefix,
	labels,
	strokeDashArray,
	nodeRadius,
	nodeScale
};
