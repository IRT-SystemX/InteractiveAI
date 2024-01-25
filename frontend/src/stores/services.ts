import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import * as servicesApi from '@/api/services'
import eventBus from '@/plugins/eventBus'
import type { Context, Entity } from '@/types/entities'
import type { Recommendations } from '@/types/services'

export const useServicesStore = defineStore('services', () => {
  const { t } = useI18n()
  const context = ref<Context | undefined>()
  const recommendations = ref<Recommendations[]>([])

  async function getContext<T extends Context>(
    entity: Entity,
    callback: (context: T) => void,
    delay = 5000
  ) {
    const modalID = crypto.randomUUID()
    let contextPID = 0
    eventBus.on('modal:close', (data) => {
      console.log('salut')
      if (data.id === modalID && data.res === 'ok') {
        handler()
        contextPID = window.setInterval(handler, delay)
      }
    })
    const handler = async () => {
      try {
        const { data } = await servicesApi.getContext()
        context.value = data.find((el) => el.use_case === entity)?.data
        if (context.value) callback(context.value as T)
      } catch (err) {
        clearInterval(contextPID)
        eventBus.emit('modal:open', {
          data: t('modal.error.CONTEXT_FAILED'),
          type: 'choice',
          id: modalID
        })
      }
    }
    handler()
    contextPID = window.setInterval(handler, delay)
  }

  async function getRecommendation<T extends Recommendations[]>(newContext?: any) {
    const payload = newContext || context.value
    const { data } = await servicesApi.getRecommendation<T>(payload)
    recommendations.value = data
  }

  return {
    context,
    recommendations,
    getContext,
    getRecommendation
  }
})
