import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as servicesApi from '@/api/services'
import eventBus from '@/plugins/eventBus'
import i18n from '@/plugins/i18n'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { FullContext, Recommendation } from '@/types/services'
import { uuid } from '@/utils/utils'

import { useCardsStore } from './cards'

const { t } = i18n.global

export const useServicesStore = defineStore('services', () => {
  const _context = ref<FullContext>()
  const _recommendations = ref<Recommendation[]>([])

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function context<T extends Entity>(entity: T) {
    return _context.value as FullContext<T>
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function recommendations<T extends Entity>(entity: T) {
    return _recommendations.value as Recommendation<T>[]
  }

  async function getContext<E extends Entity>(
    entity?: E,
    callback: (context: FullContext<E>) => void = () => {},
    delay = 5000
  ) {
    // Catch context error and reset interval
    const modalID = uuid()
    let contextPID = 0
    eventBus.on('modal:close', (data) => {
      if (data.id === modalID && data.res === 'ok') {
        handler()
        contextPID = window.setInterval(handler, delay)
      }
    })

    // Handler
    const handler = async () => {
      try {
        const { data } = await servicesApi.getContext<E>()
        if (!entity) {
          _context.value = data[0]
        }
        const res = data.find((el): el is FullContext<E> => el.use_case === entity)
        // If context is not available, return
        if (!res) return
        // If there is no previous context, set it
        if (!localStorage.getItem('context')) localStorage.setItem('context', res.id_context)
        // If previous and current context are different, we can store it and callback
        if (localStorage.getItem('context') !== res.id_context) {
          _context.value = res
          callback(res)
        }
      } catch (err) {
        clearInterval(contextPID)
        eventBus.emit('modal:open', {
          data: t('modal.error.CONTEXT_FAILED'),
          type: 'choice',
          id: modalID
        })
      }
    }
    // Start context handler immediatly
    handler()
    // Start interval handler
    contextPID = window.setInterval(handler, delay)
    return contextPID
  }

  async function getRecommendation<E extends Entity>(
    event: Card<E>['data'],
    context = _context.value as FullContext<E>
  ) {
    let curr = event
    const cardsStore = useCardsStore()
    while (curr?.parent_event_id) {
      const parent = cardsStore._cards.find(
        (card) => card.processInstanceId === curr?.parent_event_id
      )
      if (!parent) break
      curr = parent.data
    }
    const { data } = await servicesApi.getRecommendation<E>({
      event: curr.metadata,
      context: context.data
    })
    _recommendations.value = data
  }

  return {
    context,
    recommendations,
    getContext,
    getRecommendation
  }
})
