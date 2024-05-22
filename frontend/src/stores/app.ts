import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'

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
  const gutters = reactive({
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  })
  const _modals = ref<Required<Modal>[]>([])
  const _card = ref<Card>()
  const status = reactive<{
    loading: { state: 'ERROR' | 'LOADING'; data: any }[]
    context: { state: 'FROZEN' | 'ONLINE' | 'OFFLINE'; last: number }
    notifications: { state: 'ONLINE' | 'OFFLINE'; last: number }
  }>({
    loading: [],
    notifications: { state: 'OFFLINE', last: 0 },
    context: { state: 'OFFLINE', last: 0 }
  })
  const tab = reactive({
    context: 0,
    assistant: 0
  })

  function card<T extends Entity>(entity: T): Card<T> | undefined {
    return _card.value?.entityRecipients.includes(entity) ? (_card.value as Card<T>) : undefined
  }

  function addModal(modal: Modal) {
    _modals.value.push({
      id: uuid(),
      ...modal,
      callback: (res: 'ok' | 'ko', id: UUID) => {
        modal.callback?.(res, id)
        eventBus.emit('modal:close', { id, res })
      }
    })
  }

  return { _card, status, tab, gutters, card, addModal }
})
