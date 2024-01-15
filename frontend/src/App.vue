<script setup lang="ts">
import { RouterView } from 'vue-router'

import Modal from './components/atoms/Modal.vue'
import ProgressBar from './components/atoms/ProgressBar.vue'
import Navbar from './components/molecules/Navbar.vue'
import { mode } from './plugins/colorMode'

mode.value = 'auto'
</script>
<template>
  <ProgressBar />
  <Modal />
  <header>
    <Navbar />
  </header>
  <main><RouterView /></main>
</template>
