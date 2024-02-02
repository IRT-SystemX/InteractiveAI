import { useCardsStore as useCardsStorePinia } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

// by convention, composable function names start with "use"
export function useCardsStore<E extends Entity>() {
  const cardsStore = useCardsStorePinia()

  return {
    ...cardsStore,
    cards: cardsStore.cards as Card<E>[]
  }
}
