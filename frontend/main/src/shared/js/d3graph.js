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
    kpi: /App_\d+\.KPI(|_composite)\.(.*)/.exec(key)[2],
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

function t(kpi) {
  switch (kpi) {
    case 'delay_avg':
      return 'Temps de réponse';
    case 'nb_err':
      return "Nombre d'erreurs";
    case 'nb_pl':
      return 'Nombre de pages lentes';
    case 'nb_req':
      return 'Nombre de requêtes';
    case 'ratio_err':
      return "Ratio d'erreur";
    case 'ratio_pl':
      return 'Ratio de pages lentes';
  }
  return kpi;
}

function minmax(value, max = 1, min = 0) {
  return Math.min(Math.max(min, value), max);
}

export function setup(data) {
  orange_ctx_container.innerHTML = '';

  ctx.data = data;

  ctx.svg = d3
    .select(orange_ctx_container)
    .append('svg')
    .attr('width', config.width)
    .attr('height', config.height)
    .attr('id', 'orange_graph')
    .append('g');

  ctx.tooltip = d3.select(orange_ctx).append('div').attr('class', 'tooltip').style('opacity', 0);

  ctx.links = ctx.svg
    .append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(ctx.data.links)
    .enter()
    .append('line')
    .attr('class', 'link')
    .on('mouseover.tooltip', function (event, d) {
      ctx.tooltip.style('opacity', 0.9);
      ctx.tooltip
        .html(`<img slot="icon" src="./assets/images/kpi/${d.kpi}.svg">&nbsp;${t(d.kpi)} ${Math.round(d.coefficient * 100)}%`)
        .style('left', event.pageX + config.radius + 'px')
        .style('top', event.pageY + config.radius + 'px');
    })
    .on('mouseout.tooltip', function () {
      ctx.tooltip.style('opacity', 0);
    })
    .on('mousemove', function (event) {
      ctx.tooltip.style('left', event.pageX + config.radius + 'px').style('top', event.pageY + config.radius + 'px');
    });

  ctx.nodes = ctx.svg
    .append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(ctx.data.nodes)
    .enter()
    .append('g')
    .attr('class', (d) => 'node ' + ctx.statuses[d.id]?.join(' '))
    .call(
      d3
        .drag()
        .on('start', (event, d) => {
          if (!event.active) ctx.simulation.alphaTarget(0.3).restart();
          d.fy = d.y;
          d.fx = d.x;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) ctx.simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );
  ctx.nodes.append('circle').attr('r', (d) => config.radius);
  ctx.nodes
    .append('text')
    .attr('class', 'label')
    .attr('dy', '.3em')
    .text((d) => 'App ' + d.id);

  ctx.simulation = d3
    .forceSimulation()
    .force('repulsion', d3.forceCollide(config.radius * 3))
    .force('center', d3.forceCenter(config.width / 2, config.height / 2));

  ctx.simulation.nodes(ctx.data.nodes).on('tick', () => {
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
  });

  ctx.simulation.force(
    'link',
    d3
      .forceLink()
      .links(ctx.data.links)
      .distance((link) => config.force.min * link.rank)
      .id((d) => d.id)
  );

  const zoom_handler = d3
    .zoom()
    .scaleExtent([1, Infinity])
    .translateExtent([
      [0, 0],
      [config.width, config.height],
    ])
    .on('zoom', (event) => ctx.svg.attr('transform', event.transform));

  zoom_handler(d3.select(orange_ctx_container));
}

export function setStatus(node, severity) {
  if (ctx.statuses[node]) ctx.statuses[node].push(severity);
  else ctx.statuses[node] = [severity];
  ctx.nodes?.filter((d) => d.id === +node).classed(severity, true);
}

export async function setCorrelation(data, source, shown, kpi, severity) {
  ctx.rawData = data;
  config.kpi = kpi;
  setup(opfabToD3(ctx.rawData, source, shown));
  setStatus(source, severity);
}

window.setCorrelation = setCorrelation;
