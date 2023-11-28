import * as d3 from 'd3';

const config = {
  // Dimensions of the viewport
  width: 1090,
  height: 680,
  force: 200,
  radius: 50,
};

const ctx = { statuses: {} };

export function opfabToD3(data, source, shown) {
  const links = data.slice(0, shown).reduce((acc, [key, value], index) => {
    const target = +/App_(\d+).*/.exec(key)[1];
    console.debug('slt', acc);
    const link = acc.find((link) => link.source === +source && link.target === target);
    if (link) {
      link.data.push([/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)[2], value]);
      return acc;
    }
    return acc.concat({
      source: +source,
      target,
      rank: Math.floor(index / 5) + 1,
      data: [[/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)[2], value]],
    });
  }, []);

  const nodes = [...new Set(data.map(([key]) => +/App_(\d+).*/.exec(key)[1])), +source].map((key) => ({
    id: key,
    selected: key === +source,
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
        .html(
          d.data.map(([kpi, value]) => `<img slot="icon" src="./assets/images/kpi/${kpi}.svg">&nbsp;${t(kpi)} à ${Math.round(value)}%`).join('\n')
        )
        .style('left', event.pageX + 20 + 'px')
        .style('top', event.pageY + 20 + 'px');
    })
    .on('mouseout.tooltip', function () {
      ctx.tooltip.style('opacity', 0);
    })
    .on('mousemove', function (event) {
      ctx.tooltip.style('left', event.pageX + 20 + 'px').style('top', event.pageY + 20 + 'px');
    });

  ctx.nodes = ctx.svg
    .append('g')
    .attr('class', 'nodes')
    .selectAll('g')
    .data(ctx.data.nodes)
    .enter()
    .append('g')
    .attr('class', (d) => 'node ' + ctx.statuses[d.id]?.join(' '))
    .classed('focus', (d) => d.selected)
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
  ctx.nodes.append('circle').attr('r', (d) => (d.selected ? config.radius * 1.5 : config.radius));
  ctx.nodes
    .append('text')
    .attr('class', 'label')
    .attr('dy', '.3em')
    .text((d) => 'App ' + d.id);

  ctx.simulation = d3
    .forceSimulation()
    .force('repulsion', d3.forceCollide(config.radius * 2))
    .force('center', d3.forceCenter(config.width / 2, config.height / 2));

  ctx.simulation.nodes(ctx.data.nodes).on('tick', () => {
    ctx.links
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y);

    ctx.nodes.attr('transform', (d) => `translate(${d.x},${d.y})`);
  });

  ctx.simulation.force(
    'link',
    d3
      .forceLink()
      .links(ctx.data.links)
      .distance((link) => config.force * link.rank)
      .id((d) => d.id)
  );

  ctx.zoom = d3
    .zoom()
    .scaleExtent([0.1, Infinity])
    .on('zoom', (event) => ctx.svg.attr('transform', event.transform));

  ctx.zoom(d3.select(orange_ctx_container));
}

export function setStatus(node, severity) {
  if (ctx.statuses[node]) {
    ctx.statuses[node].push(severity);
  } else ctx.statuses[node] = [severity];
  ctx.nodes?.filter((d) => d.id === +node).classed(severity, true);
  if (severity === 'INFORMATION') ctx.nodes?.filter((d) => d.id === +node).classed('ACTION', false);
}

export function showLink(source, target) {
  ctx.links.classed('active', (link) => source === link.source.id && target === link.target.id);
}

export function hideLink() {
  ctx.links.classed('active', false);
}

export function showNode(id) {
  ctx.nodes.classed('focus', (node) => id === node.id);
  zoomToNode(id);
}

export function zoomToNode(id, zoom = 2) {
  const node = ctx.data.nodes.find((node) => node.id === id);
  ctx.svg
    .transition()
    .duration(750)
    .call(
      ctx.zoom.transform,
      d3.zoomIdentity
        .translate(config.width / 2, config.height / 2)
        .scale(zoom)
        .translate(-node.x, -node.y)
    );
}

export async function setCorrelation(data, source, shown, kpi, severity) {
  ctx.rawData = data;
  config.kpi = kpi;
  setup(opfabToD3(ctx.rawData, source, shown));
  setStatus(source, severity);
  setTimeout(() => zoomToNode(+source, 1.2), 200);
}

window.showLink = showLink;
window.hideLink = hideLink;
window.showNode = showNode;
window.setCorrelation = setCorrelation;
window.ctx = ctx;
window.config = config;
