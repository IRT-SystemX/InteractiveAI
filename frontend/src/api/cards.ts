import http from '@/plugins/http'
import i18n from '@/plugins/i18n'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import type { Card, CardEvent } from '@/types/cards'

let controller: AbortController = new AbortController()

const { t } = i18n.global

export async function subscribe(
  config: {
    clientId: string
    rangeEnd?: string
    rangeStart?: string
    notification?: 'true' | 'false'
  },
  handler: (card: CardEvent) => void
) {
  const authStore = useAuthStore()
  const appStore = useAppStore()
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
          case 'BUSINESS_CONFIG_CHANGE':
          case 'USER_CONFIG_CHANGE':
            break
          case 'HEARTBEAT':
            appStore.status.notifications.state = 'ONLINE'
            appStore.status.notifications.last = Date.now()
            break
          case 'DISCONNECT_USER_DUE_TO_NEW_CONNECTION':
            appStore.status.notifications.state = 'OFFLINE'
            controller.abort()
            appStore.addModal({
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

export function get(id: Card['id']) {
  return http.get<{ card: Card }>(`/cards/cards/${id}`)
}

export function update(card: any) {
  return http.post<Card>(`/cab_event/api/v1/events`, card)
}

export function remove(id: Card['id']) {
  return http.delete<null>(`/cardspub/cards/${id}`)
}

export function removeEvent(uid: Card['processInstanceId']) {
  return http.delete<null>(`/cab_event/api/v1/event/${uid}`)
}

export function acknowledge(card: Card) {
  return http.post<null>(`/cardspub/cards/userAcknowledgement/${card.uid}`, card.entityRecipients)
}

export function unsubscribe() {
  controller.abort()
}
