export const graphColors = {
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
export const icons = {
	triangle: 'M0 -12 L12 12 H-12 z',
	diamond: 'M0 -12 L12 0 L0 12 L-12 0 z',
	square: 'M-12 -12 h24 v24 h-24 z',
	hexagon: 'M12 0 L6 10.3923 L-6 10.3923 L-12 0 L-6 -10.3923 L6 -10.3923 Z',
	circle: 'M0 -12 a12 12 0 1 0 0 24 a12 12 0 1 0 0 -24 z'
};
export const graphIcons = Object.values(icons);

export const eventIcon = icons.circle;
export const exampleIcon = icons.circle;

export const labels = {
	default: 'white',
	hidden: 'transparent'
};

export const strokeDashArray = {
	default: '5, 15',
	hover: 'none'
};

export const nodeRadius = {
	default: 20,
	selected: 25,
	start: 30,
	event: 25
};

export const nodeScale = {
	default: {
		default: 1.6,
		selected: 2
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
