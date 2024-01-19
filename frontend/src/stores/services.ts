import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as servicesApi from '@/api/services'
import type { Context, Entity } from '@/types/entities'
import type { RecommendationAction } from '@/types/services'

export const useServicesStore = defineStore('services', () => {
  const context = ref<Context | undefined>()
  const recommendations = ref<any[]>([])

  async function getContext<T extends Context>(
    entity: Entity,
    callback: (context: T) => void,
    delay = 5000
  ) {
    const handler = async () => {
      const { data } = await servicesApi.getContext()
      context.value = data.find((el) => el.use_case === entity)?.data
      if (context.value) callback(context.value as T)
    }
    handler()
    return window.setInterval(handler, delay)
  }

  async function getRecommendation<T extends RecommendationAction>(newContext?: any) {
    const payload = newContext || context.value
    const { data } = await servicesApi.getRecommendation<any>(payload)
    recommendations.value = data
  }

  return {
    context,
    recommendations,
    getContext,
    getRecommendation
  }
})
