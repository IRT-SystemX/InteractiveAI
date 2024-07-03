<template>
  <Modal
    v-for="modal of appStore._modals"
    :id="modal.id"
    :key="modal.id"
    :type="modal.type"
    @close="modal.callback">
    {{ modal.data }}
  </Modal>
  <header class="p-1">
    <Navbar />
  </header>
  <main><RouterView /></main>
</template>
<script setup lang="ts">
import { RouterView } from 'vue-router'

import Modal from './components/atoms/Modal.vue'
import Navbar from './components/molecules/Navbar.vue'
import { mode } from './plugins/colorMode'
import { useAppStore } from './stores/app'

mode.value = 'auto'

const appStore = useAppStore()
</script>
