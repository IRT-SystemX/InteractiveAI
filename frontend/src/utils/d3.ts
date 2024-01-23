// @ts-nocheck
import * as d3 from 'd3'

import eventBus from '@/plugins/eventBus'

const config = {
  // Dimensions of the viewport
  width: 0,
  height: 0,
  force: 200,
  radius: 50
}

export const ctx = { statuses: {} }

export function setup(data, element: HTMLElement) {
  element.innerHTML = ''
  ctx.data = data

  ctx.svg = d3
    .select(element)
    .append('svg')
    .attr('width', element.clientWidth)
    .attr('height', element.clientHeight)
    .attr('id', 'd3-graph')
    .append('g')

  ctx.tooltip = d3.select(document.getElementById('graph-tooltip')).style('opacity', 0)

  ctx.links = ctx.svg
    .append('g')
    .attr('class', 'links')
    .selectAll('line')
    .data(ctx.data.links)
    .enter()
    .append('line')
    .attr('class', 'link')
    .on('mouseenter.tooltip', function (event, d) {
      eventBus.emit('graph:showTooltip', d.data)
      ctx.tooltip.style('opacity', 0.9)
      ctx.tooltip.style('left', event.pageX + 20 + 'px').style('top', event.pageY + 20 + 'px')
    })
    .on('mouseleave.tooltip', function () {
      ctx.tooltip.style('opacity', 0)
    })
    .on('mousemove', function (event) {
      ctx.tooltip.style('left', event.pageX + 20 + 'px').style('top', event.pageY + 20 + 'px')
    })

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
          if (!event.active) ctx.simulation.alphaTarget(0.3).restart()
          d.fy = d.y
          d.fx = d.x
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on('end', (event, d) => {
          if (!event.active) ctx.simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        })
    )
  ctx.nodes.append('circle').attr('r', (d) => (d.selected ? config.radius * 1.5 : config.radius))
  ctx.nodes
    .append('text')
    .attr('class', 'label')
    .attr('dy', '.3em')
    .text((d) => 'App ' + d.id)

  ctx.simulation = d3
    .forceSimulation()
    .force('repulsion', d3.forceCollide(config.radius * 2))
    .force('center', d3.forceCenter(config.width / 2, config.height / 2))

  ctx.simulation.nodes(ctx.data.nodes).on('tick', () => {
    ctx.links
      .attr('x1', (d) => d.source.x)
      .attr('y1', (d) => d.source.y)
      .attr('x2', (d) => d.target.x)
      .attr('y2', (d) => d.target.y)

    ctx.nodes.attr('transform', (d) => `translate(${d.x},${d.y})`)
  })

  ctx.simulation.force(
    'link',
    d3
      .forceLink()
      .links(ctx.data.links)
      .distance((link) => config.force * link.rank)
      .id((d) => d.id)
  )

  ctx.zoom = d3
    .zoom()
    .scaleExtent([0.1, Infinity])
    .on('zoom', (event) => ctx.svg.attr('transform', event.transform))

  ctx.zoom(d3.select(element))

  ctx.svg
    .transition()
    .duration(750)
    .call(
      ctx.zoom.transform,
      d3.zoomIdentity.translate(
        document.getElementById('d3-graph')?.clientWidth / 2,
        document.getElementById('d3-graph')?.clientHeight / 2
      )
    )
}

export function setStatus(node, severity) {
  if (ctx.statuses[node]) {
    ctx.statuses[node].includes(severity) && ctx.statuses[node].push(severity)
  } else ctx.statuses[node] = [severity]
  ctx.nodes?.filter((d) => d.id === +node).classed(severity, true)
  if (severity === 'INFORMATION') {
    removeStatus(node, 'ACTION')
  }
}

export function removeStatus(node, severity) {
  ctx.nodes?.filter((d) => d.id === +node).classed(severity, false)
  ctx.statuses[node](
    ctx.statuses[node].findIndex((el) => el === severity),
    1
  )
}

export function showLink(source, target) {
  ctx.links.classed('active', (link) => source === link.source.id && target === link.target.id)
}

export function hideLinks() {
  ctx.links.classed('active', false)
}

export function focusLink(source, target) {
  ctx.links.classed('focus', false)
  ctx.links.classed('focus', (link) => source === link.source.id && target === link.target.id)
  const d3link = ctx.links
    .filter((link) => source === link.source.id && target === link.target.id)
    .node()
    .getBoundingClientRect()
  eventBus.emit(
    'graph:showTooltip',
    ctx.data.links.find((link) => source === link.source.id && target === link.target.id).data
  )
  ctx.tooltip.style('opacity', 0.9)
  ctx.tooltip.style('left', d3link.x + 20 + 'px').style('top', d3link.y + 20 + 'px')
}

export function showNode(id) {
  ctx.nodes.classed('focus', (node) => id === node.id)
  zoomToNode(id)
}

export function zoomToNode(id, zoom = 1.2) {
  const node = ctx.data.nodes.find((node) => node.id === id)
  ctx.svg
    .transition()
    .duration(750)
    .call(
      ctx.zoom.transform,
      d3.zoomIdentity
        .translate(document.getElementById('cab-graph')?.clientWidth / 2, 0)
        .scale(zoom)
        .translate(-node.x, -node.y)
    )
}

export async function setCorrelation(data, source, shown, kpi, severity) {
  ctx.rawData = data
  config.kpi = kpi
  setup(opfabToD3(ctx.rawData, source, shown))
  setStatus(source, severity)
  setTimeout(() => zoomToNode(+source, 1.2), 200)
}
