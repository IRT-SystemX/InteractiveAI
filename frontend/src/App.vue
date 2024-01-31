<template>
  <ProgressBar />
  <Modal
    v-for="modal of modals"
    :id="modal.id"
    :key="modal.id"
    :data="modal.data"
    :type="modal.type"
    @close="modalClose" />
  <header>
    <Navbar />
  </header>
  <main><RouterView /></main>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'

import Modal from './components/atoms/Modal.vue'
import ProgressBar from './components/atoms/ProgressBar.vue'
import Navbar from './components/molecules/Navbar.vue'
import { mode } from './plugins/colorMode'
import eventBus from './plugins/eventBus'

mode.value = 'auto'

const modals = ref<
  {
    id: `${string}-${string}-${string}-${string}-${string}`
    data: string
    type: 'choice' | 'info'
  }[]
>([])

eventBus.on('modal:open', (message) => {
  modals.value.push({ id: crypto.randomUUID(), ...message })
})

function modalClose(id: `${string}-${string}-${string}-${string}-${string}`, res: 'ok' | 'ko') {
  console.log(id, res)
  eventBus.emit('modal:close', { id, res })
  modals.value.splice(
    modals.value.findIndex((el) => el.id === id),
    1
  )
}
</script>
