import { addDays, subDays } from 'date-fns'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as cardsApi from '@/api/cards'
import eventBus from '@/plugins/eventBus'
import i18n from '@/plugins/i18n'
import { type Card, type CardEvent, CardOperationType } from '@/types/cards'
import { type Entity } from '@/types/entities'
import { recordTraceForSession } from '@/utils/traceSessionExport'
import { uuid } from '@/utils/utils'

import { useAppStore } from './app'

const { t } = i18n.global

export const useCardsStore = defineStore('cards', () => {
  const _cards = ref<Card[]>([])

  function cards<E extends Entity>(entity: E, hasBeenAcknowledged: boolean | 'all' = false) {
    return _cards.value.filter<Card<E>>(
      (card): card is Card<E> =>
        card.entityRecipients.includes(entity) &&
        (hasBeenAcknowledged === 'all'
          ? true
          : hasBeenAcknowledged === !!card.hasBeenAcknowledged) &&
        !card.hasBeenRead
    )
  }

  async function subscribe(entity: Entity, hydrated = true) {
    const appStore = useAppStore()
    const { data } = await cardsApi.isSubscriptionActive()
    if (data) {
      appStore.addModal({
        data: t('modal.info.SUBSCRIPTION_ACTIVE'),
        type: 'choice',
        callback: (success) => {
          if (success) {
            appStore.status.notifications.state = 'ONLINE'
            _subscribe(entity, hydrated)
          } else {
            appStore.status.notifications.state = 'OFFLINE'
          }
        }
      })
    } else {
      appStore.status.notifications.state = 'ONLINE'
      _cards.value = []
      _subscribe(entity, hydrated)
    }
  }

  async function _subscribe(entity: Entity, hydrated = false) {
    const handler = async (cardEvent: CardEvent) => {
      const appStore = useAppStore()
      let existingCard = null
      if (cardEvent.type === 'ACK' && cardEvent.entitiesAcks.includes(entity))
        existingCard = _cards.value.findIndex((card) => cardEvent.cardId === card.id)
      if (cardEvent.type === 'DELETE' && cardEvent.entityRecipientsIds!.includes(entity))
        existingCard = _cards.value.findIndex((card) => cardEvent.cardId === card.id)
      if (
        cardEvent.type !== 'ACK' &&
        cardEvent.type !== 'DELETE' &&
        cardEvent.card.entityRecipients?.includes(entity)
      )
        existingCard = _cards.value.findIndex((card) => cardEvent.card.id === card.id)

      if (existingCard === null) return

      switch (cardEvent.type) {
        case CardOperationType.ADD:
        case CardOperationType.UPDATE:
          // eslint-disable-next-line no-case-declarations
          let hydratedCard: Card<Entity> | undefined = undefined
          if (hydrated) {
            const { data } = await cardsApi.get(cardEvent.card.id)
            hydratedCard = data.card
          }
          if (cardEvent.type === CardOperationType.ADD || existingCard === -1) {
            try {
              // Use hydrated card for title/summary if available (SSE notification may not include titleTranslated)
              const fullCard = hydratedCard ?? cardEvent.card
              recordTraceForSession({
                use_case: entity,
                step: 'EVENT',
                data: {
                  card_id: cardEvent.card.id,
                  process_instance_id: cardEvent.card.processInstanceId,
                  start_date: new Date(cardEvent.card.startDate).toISOString(),
                  publish_date: new Date(cardEvent.card.publishDate).toISOString(),
                  title: fullCard.titleTranslated || fullCard.title?.parameters?.title || '',
                  summary: fullCard.summaryTranslated || fullCard.summary?.parameters?.summary || '',
                  metadata: (hydratedCard ?? cardEvent.card).data.metadata
                },
                date: new Date().toISOString()
              })
            } catch (error) {
              console.warn('Unable to record EVENT trace for session export:', error)
            }
          }
          if (existingCard !== -1) {
            if (
              _cards.value[existingCard].data.criticality !== 'ND' &&
              hydratedCard?.data.criticality === 'ND'
            )
              eventBus.emit('notifications:ended', _cards.value[existingCard])
            _cards.value.splice(existingCard, 1, {
              ...cardEvent.card,
              ...hydratedCard
            })
          } else
            _cards.value.push({
              ...cardEvent.card,
              ...hydratedCard
            })
          break
        case CardOperationType.DELETE:
          if (cardEvent.cardId === appStore._card?.id) appStore._card = undefined
          _cards.value.splice(existingCard, 1)
          break
        case CardOperationType.ACK:
          if (cardEvent.cardId === appStore._card?.id) appStore._card = undefined
          _cards.value[existingCard].hasBeenAcknowledged = true
          break
      }
    }

    const id = uuid()
    cardsApi.subscribe(
      {
        clientId: id,
        rangeEnd: String(addDays(new Date(), 1).getTime()),
        rangeStart: String(subDays(new Date(), 1).getTime())
      },
      handler
    )
    cardsApi.subscribe(
      {
        clientId: id,
        notification: 'true'
      },
      handler
    )
  }

  function unsubscribe() {
    cardsApi.unsubscribe()
  }

  function acknowledge<E extends Entity = Entity>(card: Card<E>) {
    for (const children of cards(card.entityRecipients[0]))
      if (children.data.parent_event_id === card.processInstanceId) acknowledge(children)
    cardsApi.acknowledge(card)
  }

  function remove<E extends Entity = Entity>(card: Card<E>) {
    for (const children of cards(card.entityRecipients[0]))
      if (children.data.parent_event_id === card.processInstanceId) remove(children)
    cardsApi.remove(card.id)
  }

  /** Set the card's criticality to 'ND' (resolved) after the user confirms a recommendation. */
  function resolveCriticality<E extends Entity = Entity>(card: Card<E>) {
    if (card.data.criticality !== 'ND') {
      card.data.criticality = 'ND'
      eventBus.emit('notifications:ended', card)
    }
  }

  return { _cards, cards, subscribe, unsubscribe, acknowledge, remove, resolveCriticality }
})
