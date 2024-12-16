const themeStore = $state('dark');
const sidebarOpen = $state(false);
const sidebarExpanded = $state(false);

function createViewportStore() {
	let innerWidth: number = $state(0);
	let outerWidth: number = $state(0);
	let isMobile: boolean = $state(false);
	let isTablet: boolean = $state(false);
	let seeDebugPanel: boolean = $state(false);

	const actualBreakpoint: string = $derived.by(() => {
		if (innerWidth < 768) {
			return 'sm';
		} else if (innerWidth < 1024) {
			return 'md';
		}
		return 'lg';
	});

	function updateViewport(window: Window) {
		innerWidth = window.innerWidth;
		outerWidth = window.outerWidth;
		return actualBreakpoint;
	}

	return {
		get innerWidth() {
			return innerWidth;
		},
		get outerWidth() {
			return outerWidth;
		},
		get isMobile() {
			return isMobile;
		},
		set isMobile(value: boolean) {
			isMobile = value;
		},
		get isTablet() {
			return isTablet;
		},
		set isTablet(value: boolean) {
			isTablet = value;
		},
		get actualBreakpoint() {
			return actualBreakpoint;
		},
		updateViewport,
		get seeDebugPanel() {
			return seeDebugPanel;
		},
		set seeDebugPanel(value: boolean) {
			seeDebugPanel = value;
		}
	};
}

const viewportStore = createViewportStore();

export { viewportStore, themeStore, sidebarOpen, sidebarExpanded };
