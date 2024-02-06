import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as servicesApi from '@/api/services'
import eventBus from '@/plugins/eventBus'
import i18n from '@/plugins/i18n'
import type { Context, Entity } from '@/types/entities'
import type { Recommendation } from '@/types/services'

const { t } = i18n.global

export const useServicesStore = defineStore('services', () => {
  const context = ref<Context>()
  const recommendations = ref<Recommendation[]>([])

  async function getContext<E extends Entity>(
    entity: E,
    callback: (context: Context<E>) => void,
    delay = 5000
  ) {
    const modalID = crypto.randomUUID()
    let contextPID = 0
    eventBus.on('modal:close', (data) => {
      if (data.id === modalID && data.res === 'ok') {
        handler()
        contextPID = window.setInterval(handler, delay)
      }
    })
    const handler = async () => {
      try {
        const { data } = await servicesApi.getContext<E>()
        context.value = data.find((el) => el.use_case === entity)?.data
        if (context.value) callback(context.value)
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
    return contextPID
  }

  async function getRecommendation<T extends Entity = Entity>(newContext?: Context<T> | {}) {
    const payload = newContext || context.value || {}
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
