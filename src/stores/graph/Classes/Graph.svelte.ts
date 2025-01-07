import {
	drag,
	forceLink,
	forceManyBody,
	forceSimulation,
	forceX,
	forceY,
	select,
	zoom as d3Zoom,
	forceCollide
} from 'd3';
import values from '$lib/mainGraph/values';
import type { BaseType, Selection, Simulation, SimulationLinkDatum } from 'd3';
import type { BaseNode } from '$types/graph';

export const defaultGraphOptions = {
	width: 500,
	height: 500,
	alpha: 0.1,
	linkStrength: 2,
	chargeStrength: -600,
	collideRadius: 200,
	zoomEnabled: true
};
export type GraphOptions = typeof defaultGraphOptions;

export abstract class Graph<T extends BaseNode, V extends SimulationLinkDatum<T> & { source: T; target: T }> {
	_simulation: Simulation<T, undefined>;
	options: GraphOptions;

	#svg: SVGElement;
	#svgElement: Selection<SVGElement, T, null, undefined>;
	#nodeLayer: Selection<SVGGElement, T, null, undefined>;
	#linkLayer: Selection<SVGGElement, T, null, undefined>;
	#labelLayer: Selection<SVGGElement, T, null, undefined>;
	#iconLayer: Selection<SVGGElement, T, null, undefined>;

	#nodesInGraph: Selection<SVGCircleElement, T, SVGGElement, T> | undefined;
	#linksInGraph: Selection<SVGLineElement, V, SVGGElement, T> | undefined;
	#labelsInGraph: Selection<SVGTextElement, T, SVGGElement, T> | undefined;
	#iconsInGraph: Selection<SVGTextElement, T, SVGGElement, T> | undefined;

	_nodes: T[] = $state.raw([]); // lost fine-grained reactivity, but works with d3 (who doesn't like Proxys)
	#links: V[] = $derived.by(() => this.#buildLinks(this._nodes));
	selectedNode: T | null = $state.raw(null);

	constructor(canvasSvg: SVGElement, nodes: T[], options: Partial<GraphOptions> = {}) {
		this.#svg = canvasSvg;
		this.options = {
			...defaultGraphOptions,
			...options
		};
		this._nodes = nodes;

		this.#svgElement = select(canvasSvg);
		this.#svg.setAttribute('width', String(this.options.width));
		this.#svg.setAttribute('height', String(this.options.height));
		this.#svgElement.attr('width', this.options.width).attr('height', this.options.height);

		this.#linkLayer = this.#svgElement.append('g');
		this.#nodeLayer = this.#svgElement.append('g');
		this.#labelLayer = this.#svgElement.append('g');
		this.#iconLayer = this.#svgElement.append('g');

		this._simulation = forceSimulation<T>();

		// zoom
		if (this.options.zoomEnabled) {
			this.#svgElement.call(
				// @ts-expect-error d3....
				d3Zoom().on('zoom', (e) => {
					const { transform } = e;
					this.#nodeLayer.attr('transform', transform);
					this.#linkLayer.attr('transform', transform);
					this.#labelLayer.attr('transform', transform);
					this.#iconLayer.attr('transform', transform);

					const strokeWidth = 3 / Math.sqrt(transform.k);
					this.#nodeLayer.style('stroke-width', strokeWidth);
					this.#linkLayer.style('stroke-width', strokeWidth);
					this.#labelLayer.style('stroke-width', strokeWidth);
					this.#iconLayer.style('stroke-width', strokeWidth);
				})
			);
		}
	}

	init() {
		this._initSimulation();
		this.#linksInGraph = this.#updateLinksInGraph();
		this.#nodesInGraph = this.#updateNodesInGraph();
		this.#labelsInGraph = this.#updateLabelsInGraph();
		this.#iconsInGraph = this.#updateIconsInGraph();
	}

	setOptions(options: Partial<GraphOptions>) {
		this.options = {
			...this.options,
			...options
		};
		this._simulation.alpha(this.options.alpha);
		this._initSimulation();
	}

	#buildLinks(nodes: T[]) {
		const links: V[] = [];
		for (const node of nodes) {
			const parent = nodes.find((n) => n.id === node.parent);
			if (parent) {
				links.push({
					source: parent,
					target: node
				} as V);
			}
		}
		return links;
	}

	addNode(node: T) {
		this._simulation.alpha(this.options.alpha);
		const parent = this._nodes.find((n) => n.id === node.parent);
		node.x = parent?.x ?? this.options.width / 2;
		node.y = parent?.y ?? this.options.height / 2;
		this._nodes = [...this._nodes, node];
	}

	deleteNode(node: T) {
		this._simulation.alpha(this.options.alpha);
		this._nodes = this._nodes.reduce<T[]>((acc, n) => {
			if (n.parent === node.id) {
				n.parent = node.parent;
			} else if (n.id === node.id) {
				return acc;
			}
			acc.push(n);
			return acc;
		}, []);
	}

	updateNode(node: T) {
		this._simulation.alpha(this.options.alpha);
		this._nodes = this._nodes.map((n) => (n.id === node.id ? node : { ...node, ...n }));
	}

	_initSimulation = () => {
		this._simulation
			.nodes(this._nodes)
			.force(
				'link',
				forceLink<T, V>(this.#links)
					.id((d) => d.id)
					.distance((d) => {
						if (d.source.type === 'startNode' || d.target.type === 'startNode') {
							return 200;
						} else if (d.source.type === 'event' || d.target.type === 'event') {
							return 150;
						}
						return 100;
					})
					.iterations(2)
			)
			// .force('center', forceCenter(currentWidth / 2, currentHeight / 2))
			// .force('centerNode', forceRadial(100, currentWidth / 2, currentHeight / 2).strength(0.02))
			.force('charge', forceManyBody().strength(this.options.chargeStrength).theta(1).distanceMax(700))
			.force(
				'x',
				forceX<T>(this.options.width / 2).strength((d) => (d.type === 'startNode' ? 1 : 0))
			)
			.force(
				'y',
				forceY<T>(this.options.height / 2).strength((d) => (d.type === 'startNode' ? 1 : 0))
			)
			.force(
				'collide',
				forceCollide<T>().radius((d) => this.getNodeRadius(d) * 2)
			)
			.velocityDecay(0.5)
			.on('tick', () => {
				this.#linksInGraph
					?.attr('x1', (d) => String(d.source.x))
					.attr('y1', (d) => String(d.source.y))
					.attr('x2', (d) => String(d.target.x))
					.attr('y2', (d) => String(d.target.y));
				this.#nodesInGraph?.attr('cx', (d) => String(d.x)).attr('cy', (d) => String(d.y));
				this.#labelsInGraph?.attr('x', (d) => String(d.x)).attr('y', (d) => String(d.y));
				this.#iconsInGraph?.attr('x', (d) => String(d.x - this.getNodeRadius(d)*1.2/2))
        							.attr('y', (d) => String(d.y - this.getNodeRadius(d)*1.2/2));
			})
			.restart();
	};

	// Styles
	abstract getNodeIcon: (node: T) => string;
	abstract getNodeFill: (node: T) => string;
	abstract getNodeRadius: (node: T) => number;
	abstract getNodeStroke: (node: T) => string;
	abstract getLinkStroke: (link: V) => string;

	#updateLinksInGraph = () => {
		return this.#linkLayer
			.selectAll('line')
			.data(this.#links)
			.join('line')
			.attr('stroke', (d) => {
				return this.getLinkStroke(d);
			})
			.attr('stroke-opacity', 1)
			.attr('stroke-width', 1)
			.attr('stroke-linecap', 'round')
			.attr('stroke-linejoin', 'round')
			.attr('stroke-dashoffset', 0)
			.attr('stroke-dasharray', values.strokeDashArray.default) as Selection<SVGLineElement, V, SVGGElement, T>;
	};
	#updateNodesInGraph = () => {
		return this.#nodeLayer
			.selectAll('circle')
			.data(this._nodes)
			.join('circle')
			.attr('draggable', true)
			.attr('r', (d: T) => this.getNodeRadius(d))
			.style('cursor', 'pointer')
			.style('fill', (d: T) => {
				return this.getNodeFill(d);
			})
			.attr('stroke', (d: T) => this.getNodeStroke(d))
			.attr('stroke-width', 4)
			.on('mouseover', (_, d) => this.handleMouseOver(d))
			.on('mouseout', () => this.handleMouseOut())
			.call(
				// @ts-expect-error d3....
				drag<BaseType | SVGCircleElement, T>()
					.on('start', (event, d) => this.handleDragStart(event, d))
					.on('drag', (event, d) => this.handleDrag(event, d))
					.on('end', (event, d) => this.handleDragEnd(event, d))
			)
			.on('click', (_, d) => this.#selectNode(d)) as Selection<SVGCircleElement, T, SVGGElement, T>;
	};
	#updateIconsInGraph = () => {
		return this.#iconLayer
			.selectAll('image')
			.data(this._nodes)
			.join('image')
			.attr('width', (d) => String(this.getNodeRadius(d) * 1.2))
			.attr('height', (d) => String(this.getNodeRadius(d) * 1.2))
			.attr('xlink:href', (d) => this.getNodeIcon(d))
			.style('cursor', 'pointer')
			.on('click', (_, d) => this.#selectNode(d))
			.on('mouseover', (_, d) => this.handleMouseOver(d))
			.on('mouseout', () => this.handleMouseOut())
			.call(
				drag<BaseType, T>()
					.on('start', (event, d) => this.handleDragStart(event, d))
					.on('drag', (event, d) => this.handleDrag(event, d))
					.on('end', (event, d) => this.handleDragEnd(event, d))
			);
	};
	#updateLabelsInGraph = () => {
		return this.#labelLayer
			.selectAll('text')
			.data(this._nodes)
			.join('text')
			.attr('text-anchor', 'middle')
			.attr('dy', (d) => {
				return -this.getNodeRadius(d) - 5;
			})
			.style('fill', (n) => {
				if (n.type === 'hidden') {
					return values.labels.hidden;
				}
				return values.labels.default;
			})
			.style('font-size', (d) => {
				return this.getNodeRadius(d) + 'px';
			}) // TODO personalize font size
			.text((d) => d.title)
			.on('click', (_, d) => this.#selectNode(d))
			.style('cursor', 'pointer')
			.on('mouseover', (_, d) => this.handleMouseOver(d))
			.on('mouseout', () => this.handleMouseOut())
			.call(
				// @ts-expect-error d3....
				drag<BaseType, T>()
					.on('start', (event, d) => this.handleDragStart(event, d))
					.on('drag', (event, d) => this.handleDrag(event, d))
					.on('end', (event, d) => this.handleDragEnd(event, d)),
				null
			) as Selection<SVGTextElement, T, SVGGElement, T>;
	};
	#selectNode = (node: T) => {
		if (this.selectedNode?.id === node.id) {
			this.selectedNode = null;
			return;
		}
		this.selectedNode = node;
	};

	// Mouse
	handleMouseOver = (d: T) => {
		this.#linksInGraph
			?.attr('stroke', (l) => {
				if (l.source === d || l.target === d) {
					return values.graphColors.links.hover;
				}
				return this.getLinkStroke(l) ?? values.graphColors.links.default;
			})
			.attr('stroke-dasharray', (l) =>
				l.source === d || l.target === d ? values.strokeDashArray.hover : values.strokeDashArray.default
			)
			.attr('stroke-width', (l) => (l.source === d || l.target === d ? 2 : 1));

		this.#nodesInGraph?.style('fill', (n): string => {
			if (n === d) {
				return values.graphColors.nodes.selected;
			} else if (
				this.#links.some((l) => (l.source === d && l.target === n) || (l.target === d && l.source === n))
			) {
				return values.graphColors.nodes.connected;
			} else {
				return this.getNodeFill(n);
			}
		});
	};
	handleMouseOut = () => {
		this.#linksInGraph
			?.attr('stroke', (l) => {
				return this.getLinkStroke(l);
			})
			.attr('stroke-dasharray', values.strokeDashArray.default)
			.attr('stroke-width', 1);

		this.#nodesInGraph?.style('fill', (n) => {
			if (n === this.selectedNode) {
				return values.graphColors.nodes.selected;
			} else {
				return this.getNodeFill(n);
			}
		});
	};

	// Drag
	handleDragStart = (event: d3.D3DragEvent<SVGElement, T, T>, d: T) => {
		if (!event.active) this._simulation?.alphaTarget(0.1).restart();
		d.fx = d.x;
		d.fy = d.y;
	};
	handleDrag = (event: d3.D3DragEvent<SVGElement, T, T>, d: T) => {
		d.fx = event.x;
		d.fy = event.y;
	};
	handleDragEnd = (event: d3.D3DragEvent<SVGElement, T, T>, d: T) => {
		if (!event.active) this._simulation?.alphaTarget(0);
		d.fx = null;
		d.fy = null;
	};
}

export default Graph;
