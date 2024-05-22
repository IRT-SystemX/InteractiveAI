<template>
  <Modal
    v-for="modal of modals"
    :id="modal.id"
    :key="modal.id"
    :type="modal.type"
    @close="modalClose">
    {{ modal.data }}
  </Modal>
  <header class="p-1">
    <Navbar />
  </header>
  <main><RouterView /></main>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'

import Modal from './components/atoms/Modal.vue'
import Navbar from './components/molecules/Navbar.vue'
import { mode } from './plugins/colorMode'
import eventBus from './plugins/eventBus'
import type { UUID } from './types/formats'
import { uuid } from './utils/utils'

mode.value = 'auto'

const modals = ref<
  {
    id: UUID
    data: string
    type: 'choice' | 'info'
  }[]
>([])

eventBus.on('modal:open', (message) => {
  modals.value.push({ id: uuid(), ...message })
})

function modalClose(id: UUID, res: 'ok' | 'ko') {
  eventBus.emit('modal:close', { id, res })
  modals.value.splice(
    modals.value.findIndex((el) => el.id === id),
    1
  )
}
</script>
