import http from '@/plugins/http'
import { useAuthStore } from '@/stores/auth'
import type { Card, CardEvent } from '@/types/cards'
import type { CardMetadata } from '@/types/entities'

let controller: AbortController

const authStore = useAuthStore()

export async function getCardsSubscription(
  config: {
    clientId: string
    rangeEnd?: string
    rangeStart?: string
    notification?: 'true' | 'false'
  },
  handler: (card: CardEvent<CardMetadata>) => void
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
          case 'DISCONNECT_USER_DUE_TO_NEW_CONNECTION':
          case 'BUSINESS_CONFIG_CHANGE':
          case 'USER_CONFIG_CHANGE':
            break
          default:
            try {
              handler(JSON.parse(data) as CardEvent<CardMetadata>)
            } catch (err) {}
        }
      }
  }
  return response
}

export function isSubscriptionActive() {
  return http.get<boolean>('/cards/willNewSubscriptionDisconnectAnExistingSubscription')
}

export function getCard<T extends CardMetadata>(id: string) {
  return http.get<{ card: Card<T> }>(`/cards/cards/${id}`)
}

export function deleteCard(id: string) {
  http.delete(`/cardspub/cards/${id}`)
}

export function acknowledgeCard(card: Card<CardMetadata>) {
  http.post(`/cardspub/cards/userAcknowledgement/${card.uid}`, card.entityRecipients)
}

export function closeCardSubscription() {
  controller?.abort()
}
