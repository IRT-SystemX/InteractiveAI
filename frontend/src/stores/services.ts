import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as servicesApi from '@/api/services'
import type { Entity } from '@/types/entities'

export const useServicesStore = defineStore('services', () => {
  const context = ref<any>()
  const recommendations = ref<any[]>([])

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

  return {
    context,
    recommendations,
    getContext,
    getRecommendation
  }
})
