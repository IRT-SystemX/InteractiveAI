import { defineStore } from 'pinia'
import { ref } from 'vue'

import { fetchCognitiveSnapshot } from '@/api/cognitive'
import type { CognitiveSnapshot } from '@/api/cognitive'
import * as servicesApi from '@/api/services'
import i18n from '@/plugins/i18n'
import type { Card } from '@/types/cards'
import type { Context, Entity } from '@/types/entities'
import type { FullContext, Recommendation } from '@/types/services'
import { hasCognitiveConsent } from '@/utils/consent'
import { isHandlingSessionExpiry } from '@/utils/session'
import { getRootCard } from '@/utils/utils'

import { useAppStore } from './app'
import { useAuthStore } from './auth'

const { t } = i18n.global

export const useServicesStore = defineStore('services', () => {
  const _context = ref<FullContext>()
  const _recommendations = ref<Recommendation[]>([])
  /**
   * Live context-polling interval. Owned by the store so that a poll restarted
   * from the retry modal is still cancellable - components only ever saw the
   * id of the *first* interval, leaking every restarted one.
   */
  const _contextPID = ref(0)

  /** Stops context polling, whichever interval is currently live. */
  function stopContext() {
    clearInterval(_contextPID.value)
    _contextPID.value = 0
  }

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
    // Handler
    const handler = async () => {
      const appStore = useAppStore()
      try {
        const { data } = await servicesApi.getContext<E>()
        if (!entity) {
          _context.value = data[0]
        }
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
        appStore.status.context.state = 'OFFLINE'
        stopContext()
        // On session expiry the user is already being asked to log in again;
        // once logged out there is nobody to ask about retrying either
        if (isHandlingSessionExpiry() || !useAuthStore().token?.access_token) return
        useAppStore().addModal({
          data: t('modal.error.CONTEXT_FAILED'),
          type: 'choice',
          callback: (success) => {
            if (success) {
              handler()
              _contextPID.value = window.setInterval(handler, delay)
            }
          }
        })
      }
    }
    // Start context handler immediatly
    handler()
    // Start interval handler
    stopContext()
    _contextPID.value = window.setInterval(handler, delay)
    return _contextPID.value
  }

  async function getRecommendation<E extends Entity>(event: Card<E>, context = _context.value) {
    if (!context) {
      const appStore = useAppStore()
      appStore.addModal({
        data: t('modal.error.NO_CONTEXT'),
        type: 'info'
      })
      appStore._card = undefined
      appStore.tab.assistant = 0
      return
    }
    // Send the structured grid data to the RL agent, not the rendered image.
    // `context.observation` already holds the full state (topo_vect, line_status,
    // rho, load/gen, …); `context.topology` is only a ~288 KB base64 PNG used for
    // UI display. Strip it from the agent payload (a shallow copy keeps the store
    // — and therefore the UI, which reads `context.topology` — untouched).
    const contextForAgent = { ...context.data }
    if ('topology' in contextForAgent) {
      delete (contextForAgent as Record<string, unknown>).topology
    }

    // Send the latest cognitive/stress snapshot alongside event/context so the
    // RL agent can factor operator state into its recommendation — but only
    // when the operator has consented. Without consent, nothing is fetched or
    // sent to the agent. Sent as-is even on failure (snapshot may contain nulls
    // or an `error` field) so a cognitive-API outage never blocks the request.
    const payload: {
      event: Card<E>['data']['metadata']
      context: Context<E>
      cognitive_snapshot?: CognitiveSnapshot
    } = {
      event: getRootCard(event).data.metadata,
      context: contextForAgent
    }
    if (hasCognitiveConsent()) {
      payload.cognitive_snapshot = await fetchCognitiveSnapshot()
    }
    const { data } = await servicesApi.getRecommendation<E>(payload)
    _recommendations.value = data
  }

  return {
    context,
    recommendations,
    getContext,
    stopContext,
    getRecommendation
  }
})
