import { addDays, subDays } from 'date-fns'
import { defineStore } from 'pinia'
import { ref } from 'vue'

import * as cardsApi from '@/api/cards'
import eventBus from '@/plugins/eventBus'
import i18n from '@/plugins/i18n'
import {
  type Card,
  type CardEvent,
  type CardGroup,
  CardOperationType,
  type CardTree
} from '@/types/cards'
import { type Entity } from '@/types/entities'
import { uuid } from '@/utils/utils'

const { t } = i18n.global

export const useCardsStore = defineStore('cards', () => {
  const _cards = ref<Card[]>([])

  function tree<T extends Entity>(
    list: Card<T>[],
    groupBy: ((card: any) => string) | undefined,
    childKey: (card: any) => string,
    parentKey: (card: any) => string
  ) {
    const newList = [...list] as CardTree<T>[]
    const map: { [key: string]: any } = {}
    let roots: typeof groupBy extends Function ? CardGroup<T>[] : typeof newList = []
    let node, i
    if (groupBy) {
      // @ts-ignore
      roots = list.map((c) => ({ name: groupBy(c), children: [] }))
    }

    for (i = 0; i < list.length; i++) {
      map[parentKey(list[i])] = i
      newList[i].children = []
      node = list[i] as CardTree<T>
      if (childKey(node)) {
        newList[map[childKey(node)]].children.push(node)
      } else {
        roots.push(node)
      }
    }
    return roots
  }

  function cards<T extends Entity>(
    entity: T,
    hasBeenAcknowledged: boolean | 'all' = false,
    groupBy?: ((card: any) => string) | undefined,
    childKey: (card: Card) => string = (card) => card.data.parent_event_id,
    parentKey: (card: Card) => string = (card) => card.processInstanceId
  ) {
    return tree(
      [..._cards.value]
        .filter<Card<T>>(
          (card): card is Card<T> =>
            card.entityRecipients.includes(entity) &&
            (hasBeenAcknowledged === 'all'
              ? true
              : hasBeenAcknowledged === !!card.hasBeenAcknowledged) &&
            !!(
              !childKey(card) || _cards.value.find((parent) => childKey(card) === parentKey(parent))
            )
        )
        .sort((a, b) => {
          if (parentKey(a) === childKey(b)) return -1
          if (childKey(b) === parentKey(b)) return 1
          return 0
        }),
      groupBy,
      childKey,
      parentKey
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

  return { _cards, cards, subscribe, hydrate, unsubscribe }
})
