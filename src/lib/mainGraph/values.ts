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
	circle: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNpcmNsZSI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiLz48L3N2Zz4=",
	square: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNxdWFyZSI+PHJlY3Qgd2lkdGg9IjE4IiBoZWlnaHQ9IjE4IiB4PSIzIiB5PSIzIiByeD0iMiIvPjwvc3ZnPg==",
	triangle: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXRyaWFuZ2xlIj48cGF0aCBkPSJNMTMuNzMgNGEyIDIgMCAwIDAtMy40NiAwbC04IDE0QTIgMiAwIDAgMCA0IDIxaDE2YTIgMiAwIDAgMCAxLjczLTNaIi8+PC9zdmc+",
	pentagon: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXBlbnRhZ29uIj48cGF0aCBkPSJNMTAuODMgMi4zOGEyIDIgMCAwIDEgMi4zNCAwbDggNS43NGEyIDIgMCAwIDEgLjczIDIuMjVsLTMuMDQgOS4yNmEyIDIgMCAwIDEtMS45IDEuMzdINy4wNGEyIDIgMCAwIDEtMS45LTEuMzdMMi4xIDEwLjM3YTIgMiAwIDAgMSAuNzMtMi4yNXoiLz48L3N2Zz4=",
	diamond: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWRpYW1vbmQiPjxwYXRoIGQ9Ik0yLjcgMTAuM2EyLjQxIDIuNDEgMCAwIDAgMCAzLjQxbDcuNTkgNy41OWEyLjQxIDIuNDEgMCAwIDAgMy40MSAwbDcuNTktNy41OWEyLjQxIDIuNDEgMCAwIDAgMC0zLjQxbC03LjU5LTcuNTlhMi40MSAyLjQxIDAgMCAwLTMuNDEgMFoiLz48L3N2Zz4="
}

const graphIcons = [icons.circle, icons.square, icons.triangle, icons.pentagon, icons.diamond];

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
	graphIcons,
	cssSidePrefix,
	labels,
	strokeDashArray,
	nodeRadius
};
