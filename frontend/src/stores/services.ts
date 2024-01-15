import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as servicesApi from '@/api/services'
import type { Entity } from '@/types/entities'
import * as d3 from '@/utils/d3'

export const useServicesStore = defineStore('services', () => {
  const context = ref<any>()
  const recommendations = ref<any[]>([])
  const correlations = ref<{ [key: string]: { [key: string]: number } } | undefined>(undefined)
  const shown = ref(5)
  const source = ref(1)
  const formattedData = computed(() =>
    correlations.value
      ? Object.keys(correlations.value)
          .flatMap((key) => Object.entries(correlations.value![key]))
          .filter(([, value]) => value)
          .sort(([, a], [, b]) => b - a)
      : []
  )
  const d3Correlations = computed(() => {
    if (!correlations.value)
      return {
        nodes: Array.from(Array(28).keys()).map((i) => ({ id: i + 1, status: [] })),
        links: []
      }
    const links = formattedData.value.slice(0, shown.value).reduce((acc, [key, value], index) => {
      const target = +/App_(\d+).*/.exec(key)![1]
      const link = acc.find((link) => link.source === +source.value && link.target === target)
      if (link) {
        link.data.push([/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)![2], value])
        return acc
      }
      return acc.concat({
        source: +source.value,
        target,
        rank: Math.floor(index / 5) + 1,
        data: [[/App_\d+\.KPI(|_composite)\.(.*)/.exec(key)![2], value]]
      })
    }, [] as any[])

    const nodes = [
      ...new Set(formattedData.value.map(([key]) => +/App_(\d+).*/.exec(key)![1])),
      +source.value
    ].map((key) => ({
      id: key,
      selected: key === +source.value,
      status: links.find((link) => link.target === key) ? ['active'] : []
    }))

    for (const link of links) {
      d3.setStatus(link.target, 'active')
    }

    return {
      nodes,
      links
    }
  })

  async function getContext<T>(entity: Entity, callback: (context: T) => any, delay = 5000) {
    const handler = async () => {
      const { data } = await servicesApi.getContext()
      context.value = data.find((el) => el.use_case === entity)?.data
      callback(context.value)
    }
    handler()
    return window.setInterval(handler, delay)
  }

  async function getRecommendation(newContext?: any) {
    const payload = newContext || context.value
    const { data } = await servicesApi.getRecommendation(payload)
    recommendations.value = data
  }

  async function getCorrelations(params: { size: number; app_id?: string; kpi_name?: string }) {
    const { data } = await servicesApi.getCorrelations({
      size: params.size,
      app_id: params.app_id,
      kpi_name: params.kpi_name
    })
    correlations.value = data[0].data
    shown.value = 5
  }

  return {
    context,
    recommendations,
    correlations,
    shown,
    formattedData,
    d3Correlations,
    getCorrelations,
    getContext,
    getRecommendation
  }
})
