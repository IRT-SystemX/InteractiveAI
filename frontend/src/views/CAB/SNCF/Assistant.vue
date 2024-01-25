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
import type { Metadata } from '@/types/entities/SNCF'

import Default from '../Common/Assistant/Default.vue'
import Event from './Assistant/Event.vue'
import Recommendations from './Assistant/Recommendations.vue'

const card = ref<Card<Metadata>>()
const tab = ref(0)

eventBus.on('assistant:selected', (selected) => {
  card.value = selected
  tab.value = 1
})

eventBus.on('assistant:tab', (index) => {
  tab.value = index
})
</script>
