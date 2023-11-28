import * as d3 from 'd3';

const config = {
  // Dimensions of the viewport
  width: 1090,
  height: 680,
  margin: { y: 24, x: 24 },
  force: { min: 100, max: 500 }, // Max (not correlated) and min (highly correlated) distance based on their correlation coefficient
  radius: 20, // Radius of nodes in default and active state
  transition: 200, // Transition duration
};

const ctx = { statuses: {} };

export function opfabToD3(data, source, shown) {
  const links = data.slice(0, shown).map(([key, value], index) => ({
    source: +source,
    target: +/App_(\d+).*/.exec(key)[1],
    coefficient: value / 100,
    rank: Math.floor(index / 5) + 1,
    type: /App_\d+\.KPI(|_composite)\.(.*)/.exec(key)[2],
  }));

  const nodes = [...new Set(data.map(([key]) => +/App_(\d+).*/.exec(key)[1])), +source].map((key) => ({
    id: key,
    status: links.find((link) => link.target === key) ? ['active'] : [],
  }));
  for (const link of links) {
    setStatus(link.target, 'active');
  }
  return {
    nodes,
    links,
  };
}

function minmax(value, max = 1, min = 0) {
  return Math.min(Math.max(min, value), max);
}

export function setup(dataset) {
  orange_ctx_container.innerHTML = '';
  // Create a simulation for an array of nodes, and compose the desired forces.
  ctx.simulation = d3
    .forceSimulation()
    .force('repulsion', d3.forceCollide(config.radius * 2)) // Adds repulsion between nodes.
    .force('center', d3.forceCenter(config.width / 2, config.height / 2)); // Attracts nodes to the center of the svg area

  // Tooltip
  ctx.tooltip = d3.select(orange_ctx).append('div').attr('class', 'tooltip').style('opacity', 0);

  // Main SVG
  ctx.svg = d3
    .select(orange_ctx_container)
    .append('svg')
    .attr('width', config.width)
    .attr('height', config.height)
    .attr('id', 'orange_graph')
    .append('g');

  // Create data
  ctx.dataset = dataset;

  // Initialize the links
  ctx.links = ctx.svg
    .append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(ctx.dataset.links)
    .enter()
    .append('line')
    .attr('class', 'link')
    .on('mouseover.tooltip', function (event, d) {
      ctx.tooltip.style('opacity', 0.9);
      ctx.tooltip
        .html(`App ${d.source.id} corrélé à App ${d.target.id} à ${Math.round(d.coefficient * 100)}%`)
        .style('left', event.pageX + config.radius + 'px')
        .style('top', event.pageY + config.radius + 'px');
    })
    .on('mouseout.tooltip', function () {
      ctx.tooltip.style('opacity', 0);
    })
    .on('mousemove', function (event) {
      ctx.tooltip.style('left', event.pageX + config.radius + 'px').style('top', event.pageY + config.radius + 'px');
    });

  // Initialize the nodes
  ctx.nodes = ctx.svg
    .append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(ctx.dataset.nodes)
    .enter()
    .append('g')
    .attr('class', (d) => 'node ' + ctx.statuses[d.id]?.join(' '))
    .call(
      d3
        .drag() // Sets the event listener for the specified typenames and returns the drag behavior.
        .on('start', dragstarted) // Start - after a new pointer becomes active (on mousedown or touchstart).
        .on('drag', dragged) // Drag - after an active pointer moves (on mousemove or touchmove).
        .on('end', dragended) // End - after an active pointer becomes inactive (on mouseup, touchend or touchcancel).
    );

  ctx.nodes.append('circle').attr('r', (d) => config.radius);
  ctx.nodes
    .append('text')
    .attr('class', 'label')
    .attr('dy', '.3em')
    .text((d) => 'App ' + d.id);

  // Listen for tick events to render the nodes as they update in your Canvas or SVG.
  ctx.simulation
    .nodes(ctx.dataset.nodes) // Sets the simulation’s nodes to the specified array of objects, initializing their positions and velocities, and then re-initializes any bound forces;
    .on('tick', ticked); // Use simulation.on to listen for tick events as the simulation runs.
  // After this, Each node must be an object. The following properties are assigned by the simulation:
  // index - the node’s zero-based index into nodes
  // x - the node’s current x-position
  // y - the node’s current y-position
  // vx - the node’s current x-velocity
  // vy - the node’s current y-velocity

  ctx.simulation.force(
    'link',
    d3
      .forceLink() // This force provides links between nodes
      .links(ctx.dataset.links)
      .distance((link) => config.force.min * link.rank)
      .id((d) => d.id) // This sets the node id accessor to the specified function. If not specified, will default to the index of a node.
  );

  // This function is run at each iteration of the force algorithm, updating the nodes position (the nodes data array is directly manipulated).
  function ticked() {
    ctx.links
      .attr('x1', (d) => minmax(d.source.x, config.width - config.margin.x, config.margin.x))
      .attr('y1', (d) => minmax(d.source.y, config.height - config.margin.y, config.margin.y))
      .attr('x2', (d) => minmax(d.target.x, config.width - config.margin.x, config.margin.x))
      .attr('y2', (d) => minmax(d.target.y, config.height - config.margin.y, config.margin.y));

    ctx.nodes.attr(
      'transform',
      (d) =>
        `translate(${minmax(d.x, config.width - config.margin.x, config.margin.x)},${minmax(d.y, config.height - config.margin.y, config.margin.y)})`
    );
  }

  // Create zoom handler
  const zoom_handler = d3
    .zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([
      [0, 0],
      [config.width, config.height],
    ])
    .on('zoom', zoom_actions);

  // Specify what to do when zoom event listener is triggered
  function zoom_actions(event) {
    ctx.svg.attr('transform', event.transform);
  }

  // Add zoom behaviour to the svg element
  // Same as svg.call(zoom_handler);
  zoom_handler(d3.select(orange_ctx_container));

  // When the drag gesture starts, the targeted node is fixed to the pointer
  // The simulation is temporarily “heated” during interaction by setting the target alpha to a non-zero value.
  function dragstarted(event, d) {
    if (!event.active) ctx.simulation.alphaTarget(0.3).restart(); // Sets the current target alpha to the specified number in the range [0,1].
    d.fy = d.y; // Fx - the node’s fixed x-position. Original is null.
    d.fx = d.x; // Fy - the node’s fixed y-position. Original is null.
  }

  // When the drag gesture starts, the targeted node is fixed to the pointer
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  // The targeted node is released when the gesture ends
  function dragended(event, d) {
    if (!event.active) ctx.simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

export function setStatus(node, severity) {
  if (ctx.statuses[node]) ctx.statuses[node].push(severity);
  else ctx.statuses[node] = [severity];
  ctx.nodes?.filter((d) => d.id === +node).classed(severity, true);
}

export async function setCorrelation(data, source, shown, kpi, severity) {
  orange_ctx_container.innerHTML = 'Loading';

  ctx.data = data;
  config.kpi = kpi;
  setup(opfabToD3(ctx.data, source, shown));
  setStatus(source, severity);
}

window.setCorrelation = setCorrelation;
