import {
  drag,
  forceCenter,
  forceCollide,
  forceLink,
  forceSimulation,
  select,
  zoom,
  zoomIdentity
} from 'd3'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import type { CorrelationData, CorrelationKey, KPI } from '@/entities/ORANGE/types'
import eventBus from '@/plugins/eventBus'
import { type Card, CriticalityArray } from '@/types/cards'
import type { Link, Node } from '@/types/components/graph'

export const useGraphStore = defineStore('graph', () => {
  const data = ref<{
    nodes: Node[]
    links: Link[]
  }>()
  const correlations = ref<CorrelationData>()
  const shown = ref(5)

  const formattedData = computed(() =>
    correlations.value
      ? (Object.keys(correlations.value)
          .flatMap((key) =>
            Object.entries(correlations.value![key as keyof typeof correlations.value])
          )
          .filter(([, value]) => value)
          .sort(([, a], [, b]) => Number(b) - Number(a)) as [CorrelationKey, number][])
      : []
  )
  function d3Correlations(source: number) {
    if (!correlations.value)
      return {
        nodes: Array.from(Array(28).keys()).map((i) => ({
          id: i + 1,
          status: [],
          selected: false
        })),
        links: []
      }
    const links = formattedData.value
      .slice(0, shown.value)
      .reduce<Link[]>((acc, [key, value], index) => {
        const target = +/\d+/.exec(key)![0]
        const link = acc.find((link) => link.source === source && link.target === target)
        if (link) {
          link.data.push([/.*?\d+\.KPI(|_composite)\.(.*)/.exec(key)![2], value])
          return acc
        }
        return acc.concat({
          source,
          target,
          rank: Math.floor(index / 5) + 1,
          data: [[/.*?\d+\.KPI(|_composite)\.(.*)/.exec(key)![2], value]]
        })
      }, [])

    const nodes = [
      ...new Set(formattedData.value.map(([key]) => +/\d+/.exec(key)![0])),
      source
    ].map((key) => ({
      id: key,
      selected: key === source,
      status: links.find((link) => link.target === key) ? ['active'] : []
    }))

    for (const link of links) {
      ctx.nodes?.filter((d: Node) => d.id === +link).classed('active', true)
    }

    const res = { nodes, links: links.sort((a, b) => b.rank - a.rank) } as {
      nodes: Node[]
      links: Link[]
    }
    data.value = res

    return res
  }

  // Utilities
  const config = {
    // Dimensions of the viewport
    width: 0,
    height: 0,
    force: 200,
    radius: 50,
    kpi: 'ratio_err'
  }

  const ctx: {
    statuses: { [k: Node['id']]: Node['status'] }
    data?: { nodes: Node[]; links: Link[] }
    svg?: any
    simulation?: any
    tooltip?: any
    nodes?: any
    links?: any
    zoom?: any
    rawData?: any
  } = { statuses: {} }

  function setup(data: { nodes: Node[]; links: Link[] }, element: HTMLElement) {
    element.innerHTML = ''
    ctx.data = data

    ctx.svg = select(element)
      .append('svg')
      .attr('width', element.clientWidth)
      .attr('height', element.clientHeight)
      .attr('id', 'd3-graph')
      .append('g')

    ctx.tooltip = select(document.getElementById('graph-tooltip')).style('opacity', 0)

    ctx.links = ctx.svg
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(ctx.data.links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .style('stroke', (d: any) => {
        return `color-mix(in srgb, var(--color-primary) ${(1 - d.rank / 10) * 100}%, #BCCAD1)`
      })
      .on('mouseenter.tooltip', function (event: MouseEvent, d: Link) {
        eventBus.emit('graph:showTooltip', {
          app: d.target,
          correlations: d.data
        })
        ctx.tooltip.style('opacity', 0.9)
        ctx.tooltip.style('left', event.pageX + 20 + 'px').style('top', event.pageY + 20 + 'px')
      })
      .on('mouseleave.tooltip', function () {
        ctx.tooltip.style('opacity', 0)
      })
      .on('mousemove', function (event: MouseEvent) {
        ctx.tooltip.style('left', event.pageX + 20 + 'px').style('top', event.pageY + 20 + 'px')
      })

    ctx.nodes = ctx.svg
      .append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(ctx.data.nodes)
      .enter()
      .append('g')
      .attr('class', (d: Node) => 'node ' + ctx.statuses[d.id]?.join(' '))
      .classed('focus', (d: Node) => d.selected)
      .call(
        drag<SVGGElement, Node>()
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
    ctx.nodes
      .append('circle')
      .attr('r', (d: Node) => (d.selected ? config.radius * 1.5 : config.radius))
    ctx.nodes
      .append('text')
      .attr('class', 'label')
      .attr('dy', '.3em')
      .text((d: Node) => 'App ' + d.id)

    ctx.simulation = forceSimulation()
      .force('repulsion', forceCollide(config.radius * 2))
      .force('center', forceCenter(config.width / 2, config.height / 2))

    ctx.simulation.nodes(ctx.data.nodes).on('tick', () => {
      ctx.links
        .attr('x1', (d: Link) => typeof d.source === 'object' && d.source.x)
        .attr('y1', (d: Link) => typeof d.source === 'object' && d.source.y)
        .attr('x2', (d: Link) => typeof d.target === 'object' && d.target.x)
        .attr('y2', (d: Link) => typeof d.target === 'object' && d.target.y)
      ctx.nodes.attr('transform', (d: Node) => `translate(${d.x},${d.y})`)
    })

    ctx.simulation.force(
      'link',
      forceLink<Node, Link>()
        .links(ctx.data.links)
        .distance((link) => config.force * link.rank)
        .id((d) => d.id)
    )

    ctx.zoom = zoom()
      .scaleExtent([0.1, Infinity])
      .on('zoom', (event) => ctx.svg.attr('transform', event.transform))

    ctx.zoom(select(element))

    ctx.svg.call(
      ctx.zoom.transform,
      zoomIdentity.translate(
        document.getElementById('d3-graph')!.clientHeight / 2,
        document.getElementById('d3-graph')!.clientWidth / 2
      )
    )
  }

  function setStatuses(cards: Card<'ORANGE'>[]) {
    for (const criticality of CriticalityArray) {
      ctx.nodes.classed(criticality, false)
    }
    for (const card of cards) {
      ctx.nodes
        ?.filter((d: Node) => d.id === +/\d+/.exec(card.data.metadata.id_app)![0])
        .classed(card.data.criticality, true)
    }
  }

  function showLink(source: Node['id'], target: Node['id']) {
    ctx.links.classed(
      'active',
      (link: Link) =>
        typeof link.source === 'object' &&
        source === link.source.id &&
        typeof link.target === 'object' &&
        target === link.target.id
    )
  }

  function hideLinks() {
    ctx.links.classed('active', false)
  }

  function focusLink(source: Node['id'], target: Node['id']) {
    ctx.links.classed('focus', false)
    ctx.links.classed(
      'focus',
      (link: Link) =>
        typeof link.source === 'object' &&
        source === link.source.id &&
        typeof link.target === 'object' &&
        target === link.target.id
    )
    const d3link = ctx.links
      .filter(
        (link: Link) =>
          typeof link.source === 'object' &&
          source === link.source.id &&
          typeof link.target === 'object' &&
          target === link.target.id
      )
      .node()
      .getBoundingClientRect()
    eventBus.emit('graph:showTooltip', {
      app: target,
      correlations: ctx.data!.links.find(
        (link) =>
          typeof link.source === 'object' &&
          source === link.source.id &&
          typeof link.target === 'object' &&
          target === link.target.id
      )!.data
    })
    ctx.tooltip.style('opacity', 0.9)
    ctx.tooltip.style('left', d3link.x + 20 + 'px').style('top', d3link.y + 20 + 'px')
  }

  function showNode(id: Node['id']) {
    ctx.nodes.classed('focus', (node: Node) => id === node.id)
    zoomToNode(id)
  }

  function zoomToNode(id: Node['id'], zoom = 1.2) {
    const node = ctx.data!.nodes.find((node) => node.id === id)
    ctx.svg
      .transition()
      .duration(750)
      .call(
        ctx.zoom.transform,
        zoomIdentity
          .translate(
            -node!.x! + document.getElementById('d3-graph')!.clientWidth / 2,
            -node!.y! + document.getElementById('d3-graph')!.clientHeight / 2
          )
          .scale(zoom)
      )
  }

  async function setCorrelation(
    data: { nodes: Node[]; links: Link[] },
    source: number,
    kpi: KPI,
    element: HTMLElement,
    cards: Card<'ORANGE'>[]
  ) {
    ctx.rawData = data
    config.kpi = kpi
    setup(d3Correlations(source), element)
    setStatuses(cards)
    setTimeout(() => zoomToNode(+source, 1.2), 200)
  }

  return {
    data,
    correlations,
    shown,
    formattedData,
    setup,
    d3Correlations,
    zoomToNode,
    setStatuses,
    showLink,
    hideLinks,
    focusLink,
    showNode,
    setCorrelation
  }
})
