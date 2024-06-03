import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'

import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { UUID } from '@/types/formats'
import { uuid } from '@/utils/utils'

type Modal = {
  id?: UUID
  data: string
  type: 'choice' | 'info'
  callback?: (success: boolean) => void
}

export const useAppStore = defineStore('app', () => {
  const panels = reactive({
    right: true,
    bottom: true,
    left: true
  })
  const _modals = ref<Required<Modal>[]>([])
  const _card = ref<Card>()
  const status = reactive<{
    requests: { state: 'ERROR' | 'LOADING'; data: any }[]
    notifications: { state: 'ONLINE' | 'OFFLINE'; last: number }
    context: { state: 'FROZEN' | 'ONLINE' | 'OFFLINE' | 'NONE'; last: number }
  }>({
    requests: [],
    notifications: { state: 'OFFLINE', last: 0 },
    context: { state: 'NONE', last: 0 }
  })
  const tab = reactive({
    context: 0,
    assistant: 0
  })

  function $reset() {
    _card.value = undefined
    tab.context = 0
    tab.assistant = 0
  }

  const requestsStatus = computed(() =>
    status.requests.reduce((acc, el) => (acc = acc !== 'ERROR' ? el.state : acc), 'IDLE')
  )

  function card<E extends Entity>(entity: E): Card<E> | undefined {
    return _card.value?.entityRecipients.includes(entity) ? (_card.value as Card<E>) : undefined
  }

  function addModal(modal: Omit<Modal, 'id'>) {
    const id = uuid()
    _modals.value.push({
      id,
      ...modal,
      callback: (success) => {
        modal.callback?.(success)
        _modals.value.splice(
          _modals.value.findIndex((el) => el.id === id),
          1
        )
      }
    })
  }

  return { _modals, _card, status, requestsStatus, tab, panels, card, addModal, $reset }
})
