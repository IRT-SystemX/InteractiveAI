import { defineStore } from 'pinia'
import { ref } from 'vue'

import eventBus from '@/plugins/eventBus'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { UUID } from '@/types/formats'
import { uuid } from '@/utils/utils'

type Modal = {
  id?: UUID
  data: string
  type: 'choice' | 'info'
  callback?: (res: 'ok' | 'ko', id: UUID) => void
}

export const useAppStore = defineStore('app', () => {
  const gutters = ref<{
    top: number
    right: number
    bottom: number
    left: number
  }>({
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  })
  const globalModals = ref<Required<Modal>[]>([])
  const _selectedCard = ref<Card>()
  const contextTab = ref(0)
  const assistantTab = ref(0)

  function selectedCard<T extends Entity>(entity: T): Card<T> | undefined {
    return _selectedCard.value?.entityRecipients.includes(entity)
      ? (_selectedCard.value as Card<T>)
      : undefined
  }

  function addModal(modal: Modal) {
    globalModals.value.push({
      id: uuid(),
      ...modal,
      callback: (res: 'ok' | 'ko', id: UUID) => {
        modal.callback?.(res, id)
        eventBus.emit('modal:close', { id, res })
      }
    })
  }

  return { assistantTab, contextTab, gutters, selectedCard, addModal }
})
