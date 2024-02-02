import { useCardsStore as useCardsStorePinia } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function useCardsStore<E extends Entity>(entity: E) {
  const cardsStore = useCardsStorePinia()

  return {
    ...cardsStore,
    cards: cardsStore.cards as Card<E>[]
  }
}
