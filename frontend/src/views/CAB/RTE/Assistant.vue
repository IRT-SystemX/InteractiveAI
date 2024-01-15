<template>
  <section class="cab-panel">
    <Default>
      <Event v-if="tab === 1 && card" :card="card" />
      <Recommendations v-if="tab === 2 && card" :card="card" />
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import eventBus from '@/plugins/eventBus'
import type { Card } from '@/types/cards'

import Default from '../Common/Assistant/Default.vue'
import Event from './Assistant/Event.vue'
import Recommendations from './Assistant/Recommendations.vue'

const card = ref<Card | undefined>(undefined)

const tab = ref(0)

eventBus.on('assistant:selectedCard', (selectedCard) => {
  card.value = selectedCard
  tab.value = 1
})
eventBus.on('assistant:tab', (index) => {
  tab.value = index
})
</script>
<style lang="scss"></style>
