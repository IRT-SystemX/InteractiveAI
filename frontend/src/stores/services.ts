import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as servicesApi from '@/api/services'
import i18n from '@/plugins/i18n'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { FullContext, Recommendation } from '@/types/services'

import { useAppStore } from './app'
import { useCardsStore } from './cards'

const { t } = i18n.global

export const useServicesStore = defineStore('services', () => {
  const _context = ref<FullContext>()
  const _recommendations = ref<Recommendation[]>([])

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function context<E extends Entity>(entity: E) {
    return _context.value as FullContext<E> | undefined
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  function recommendations<E extends Entity>(entity: E) {
    return _recommendations.value as Recommendation<E>[]
  }

  async function getContext<E extends Entity>(
    entity?: E,
    callback: (context: FullContext<E>) => void = () => {},
    delay = 5000
  ) {
    // Catch context error and reset interval
    let contextPID = 0
    // Handler
    const handler = async () => {
      try {
        const { data } = await servicesApi.getContext<E>()
        if (!entity) {
          _context.value = data[0]
        }
        const appStore = useAppStore()
        const res = data.find((el): el is FullContext<E> => el.use_case === entity)
        // If context is not available, return
        if (!res) {
          appStore.status.context.state = 'OFFLINE'
          return
        }
        // If there is no previous context, set it
        if (!localStorage.getItem('context')) localStorage.setItem('context', res.id_context)
        // If previous and current context are different, we can store it and callback
        if (
          localStorage.getItem('context') !== res.id_context &&
          res.id_context !== _context.value?.id_context
        ) {
          _context.value = res
          appStore.status.context.state = 'ONLINE'
          callback(res)
        } else {
          appStore.status.context.state = 'FROZEN'
        }
        appStore.status.context.last = Date.now()
      } catch (err) {
        clearInterval(contextPID)
        useAppStore().addModal({
          data: t('modal.error.CONTEXT_FAILED'),
          type: 'choice',
          callback: (success) => {
            if (success) {
              handler()
              contextPID = window.setInterval(handler, delay)
            }
          }
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
    context = _context.value
  ) {
    const cardsStore = useCardsStore()
    let curr = event
    while (curr?.parent_event_id) {
      const parent = cardsStore._cards.find(
        (card) => card.processInstanceId === curr?.parent_event_id
      )
      if (!parent) break
      curr = parent.data
    }
    if (!context) return
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
