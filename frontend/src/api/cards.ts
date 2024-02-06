import eventBus from '@/plugins/eventBus'
import http from '@/plugins/http'
import i18n from '@/plugins/i18n'
import { useAuthStore } from '@/stores/auth'
import type { Card, CardEvent } from '@/types/cards'

let controller: AbortController = new AbortController()

const authStore = useAuthStore()
const { t } = i18n.global

export async function getCardsSubscription(
  config: {
    clientId: string
    rangeEnd?: string
    rangeStart?: string
    notification?: 'true' | 'false'
  },
  handler: (card: CardEvent) => void
) {
  controller = new AbortController()
  const response = await fetch(
    import.meta.env.VITE_API +
      '/cards/cardSubscription?' +
      new URLSearchParams({
        ...config,
        version: 'SNAPSHOT'
      }),
    {
      headers: {
        Authorization: `Bearer ${authStore.token?.access_token}`
      },
      method: 'GET',
      signal: controller.signal
    }
  )
  const reader = response.body!.getReader()
  const decoder = new TextDecoder('utf-8')
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    const raw = decoder.decode(value)
    for (const payload of raw.split('\n'))
      if (payload.slice(0, 5) === 'data:') {
        const data = payload.slice(5)
        switch (data) {
          case 'INIT':
          case 'RELOAD':
          case 'HEARTBEAT':
          case 'BUSINESS_CONFIG_CHANGE':
          case 'USER_CONFIG_CHANGE':
            break
          case 'DISCONNECT_USER_DUE_TO_NEW_CONNECTION':
            controller.abort()
            eventBus.emit('modal:open', {
              data: t(`modal.error.DISCONNECT_USER_DUE_TO_NEW_CONNECTION`),
              type: 'info'
            })
            break
          default:
            try {
              handler(JSON.parse(data) as CardEvent)
            } catch (err) {}
        }
      }
  }
  return response
}

export function isSubscriptionActive() {
  return http.get<boolean>('/cards/willNewSubscriptionDisconnectAnExistingSubscription')
}

export function getCard(id: string) {
  return http.get<{ card: Card }>(`/cards/cards/${id}`)
}

// TODO: typing
export function deleteCard(id: string) {
  http.delete(`/cardspub/cards/${id}`)
}

// TODO: typing
export function acknowledgeCard(card: Card) {
  http.post(`/cardspub/cards/userAcknowledgement/${card.uid}`, card.entityRecipients)
}

export function closeCardSubscription() {
  controller.abort()
}
