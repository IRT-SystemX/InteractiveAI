import { addDays, subDays } from 'date-fns'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as cardsApi from '@/api/cards'
import eventBus from '@/plugins/eventBus'
import i18n from '@/plugins/i18n'
import { type Card, type CardEvent, CardOperationType, type CardTree } from '@/types/cards'
import { type Entity } from '@/types/entities'
import { uuid } from '@/utils/utils'

const { t } = i18n.global

export const useCardsStore = defineStore('cards', () => {
  const _cards = ref<Card[]>([])

  function tree<T extends Entity>(list: Card<T>[]) {
    const newList = [...list].sort((a, b) => {
      if (a.processInstanceId === b.data.parent_event_id) return -1
      if (a.data.parent_event_id === b.processInstanceId) return 1
      return 0
    }) as CardTree<T>[]
    const map: { [key: string]: any } = {},
      roots = []
    let node, i

    for (i = 0; i < newList.length; i++) {
      map[newList[i].processInstanceId] = i
      newList[i].children = []
      node = newList[i] as CardTree<T>
      if (node.data.parent_event_id) {
        newList[map[node.data.parent_event_id]].children.push(node)
      } else {
        roots.push(node)
      }
    }
    return roots
  }

  function cards<T extends Entity>(entity: T, hasBeenAcknowledged: boolean | 'all' = false) {
    return _cards.value.filter<Card<T>>(
      (card): card is Card<T> =>
        card.entityRecipients.includes(entity) &&
        (hasBeenAcknowledged === 'all' ? true : hasBeenAcknowledged === !!card.hasBeenAcknowledged)
    )
  }

  async function subscribe(entity: Entity, hydrated = true) {
    _cards.value = []
    const { data } = await cardsApi.isSubscriptionActive()
    if (data) {
      const id = uuid()
      eventBus.emit('modal:open', {
        id,
        data: t('modal.info.SUBSCRIPTION_ACTIVE'),
        type: 'choice'
      })
      eventBus.on(
        'modal:close',
        (data) => data.id === id && data.res === 'ok' && _subscribe(entity, hydrated)
      )
    } else {
      _subscribe(entity, hydrated)
    }
  }

  async function _subscribe(entity: Entity, hydrated = false) {
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
          // eslint-disable-next-line no-case-declarations
          let hydratedCard: Card<Entity> | undefined = undefined
          if (hydrated) {
            const { data } = await cardsApi.get(cardEvent.card.id)
            hydratedCard = data.card
          }
          if (existingCard !== -1) {
            if (
              _cards.value[existingCard].data.criticality !== 'ND' &&
              hydratedCard?.data.criticality === 'ND'
            )
              eventBus.emit('notifications:close', _cards.value[existingCard])
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
          _cards.value.splice(existingCard, 1)
          break
        case CardOperationType.ACK:
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
    cardsApi
      .subscribe(
        {
          clientId: id,
          notification: 'true'
        },
        handler
      )
      .finally(() => (_cards.value = []))
  }

  function unsubscribe() {
    cardsApi.unsubscribe()
    _cards.value = []
  }

  async function hydrate(id: string) {
    const { data } = await cardsApi.get(id)
    const i = _cards.value.findIndex((card) => card.id === data.card.id)
    if (i !== -1) {
      _cards.value[i] = { ..._cards.value[i], ...data.card }
    } else {
      _cards.value.push(data.card)
    }
  }

  return { _cards, tree, cards, subscribe, hydrate, unsubscribe }
})
