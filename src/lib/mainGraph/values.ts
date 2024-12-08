const cssSidePrefix = 'side-';

const graphColors = {
	nodes: {
		// hex colors or color names
		sides: ['blue', 'red', 'green', 'cyan', 'pink'],
		selected: 'white',
		start: '#FFF0FF',
		event: '#0FF0F0',
		connected: '#FF00FF',
		hidden: 'black'
	},
	links: {
		default: 'white',
		hover: '#FF0000',
		toHide: 'gray'
	}
};

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

export default {
	graphColors,
	cssSidePrefix,
	labels,
	strokeDashArray,
	nodeRadius
};
