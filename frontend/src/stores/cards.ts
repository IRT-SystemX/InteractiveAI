import { endOfDay, startOfDay } from 'date-fns'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as cardsApi from '@/api/cards'
import eventBus from '@/plugins/eventBus'
import i18n from '@/plugins/i18n'
import { type Card, type CardEvent, CardOperationType } from '@/types/cards'
import type { Entity } from '@/types/entities'

const { t } = i18n.global

export const useCardsStore = defineStore('cards', () => {
  const _cards = ref<Card[]>([])

  function cards<T extends Entity>(entity: T) {
    return _cards.value.filter<Card<T>>((card): card is Card<T> =>
      card.entityRecipients.includes(entity)
    )
  }

  async function getCards(entity: Entity, hydrated = false) {
    _cards.value = []
    const { data } = await cardsApi.isSubscriptionActive()
    if (data) {
      const id = crypto.randomUUID()
      eventBus.emit('modal:open', {
        id,
        data: t('modal.info.SUBSCRIPTION_ACTIVE'),
        type: 'choice'
      })
      eventBus.on(
        'modal:close',
        (data) => data.id === id && data.res === 'ok' && _getCards(entity, hydrated)
      )
    } else {
      _getCards(entity, hydrated)
    }
  }

  async function _getCards(entity: Entity, hydrated = false) {
    const handler = async (cardEvent: CardEvent) => {
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
          if (cardEvent.card.hasBeenAcknowledged) return
          // eslint-disable-next-line no-case-declarations
          let hydratedCard = {}
          if (hydrated) {
            const { data } = await cardsApi.getCard(cardEvent.card.id)
            hydratedCard = data.card
          }
          if (existingCard !== -1)
            _cards.value.splice(existingCard, 1, {
              ...cardEvent.card,
              ...hydratedCard,
              hydrated
            })
          else
            _cards.value.push({
              ...cardEvent.card,
              ...hydratedCard,
              hydrated
            })
          break
        case CardOperationType.DELETE:
          _cards.value.splice(existingCard, 1)
          break
        case CardOperationType.ACK:
          _cards.value.splice(existingCard, 1)
          break
      }
    }

    const id = crypto.randomUUID()
    cardsApi.getCardsSubscription(
      {
        clientId: id,
        rangeEnd: String(endOfDay(new Date()).getTime()),
        rangeStart: String(startOfDay(new Date()).getTime())
      },
      handler
    )
    cardsApi
      .getCardsSubscription(
        {
          clientId: id,
          notification: 'true'
        },
        handler
      )
      .finally(() => (_cards.value = []))
  }

  function closeCards() {
    cardsApi.closeCardSubscription()
    _cards.value = []
  }

  async function hydrateCard(id: string) {
    const { data } = await cardsApi.getCard(id)
    const i = _cards.value.findIndex((card) => card.id === data.card.id)
    if (i !== -1) {
      _cards.value[i] = { ..._cards.value[i], ...data.card }
    } else {
      _cards.value.push(data.card)
    }
  }

  return { cards, getCards, hydrateCard, closeCards }
})
