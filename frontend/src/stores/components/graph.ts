import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as d3 from '@/utils/d3'

export const useGraphStore = defineStore('graph', () => {
  const data = ref<{ nodes: any[]; links: any[] }>()
  const correlations = ref<{ [key: string]: { [key: string]: number } }>()
  const shown = ref(5)

  const formattedData = computed(() =>
    correlations.value
      ? Object.keys(correlations.value)
          .flatMap((key) => Object.entries(correlations.value![key]))
          .filter(([, value]) => value)
          .sort(([, a], [, b]) => b - a)
      : []
  )
  function d3Correlations(source = 1) {
    if (!correlations.value)
      return {
        nodes: Array.from(Array(28).keys()).map((i) => ({ id: i + 1, status: [] })),
        links: []
      }
    const links = formattedData.value.slice(0, shown.value).reduce((acc, [key, value], index) => {
      const target = +/App_(\d+).*/.exec(key)![1]
      const link = acc.find((link) => link.source === source && link.target === target)
      if (link) {
        link.data.push([/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)![2], value])
        return acc
      }
      return acc.concat({
        source,
        target,
        rank: Math.floor(index / 5) + 1,
        data: [[/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)![2], value]]
      })
    }, [] as any[])

    const nodes = [
      ...new Set(formattedData.value.map(([key]) => +/App_(\d+).*/.exec(key)![1])),
      source
    ].map((key) => ({
      id: key,
      selected: key === source,
      status: links.find((link) => link.target === key) ? ['active'] : []
    }))

    for (const link of links) {
      d3.setStatus(link.target, 'active')
    }
    data.value = {
      nodes,
      links
    }
    return {
      nodes,
      links
    }
  }

  return { data, correlations, shown, formattedData, d3Correlations }
})
