<template>
  <section class="cab-panel">
    <Default>
      <Event v-if="tab === 1 && card" :card="card" />
      <Recommendations
        v-if="tab === 2"
        :recommendations="servicesStore.recommendations"
        :buttons="[$t('recommendations.button1'), $t('recommendations.button2')]"
        @selected="onSelection">
        <template #default="{ recommendation }">
          <div class="flex">
            <aside class="flex flex-center mr-1">
              <Star stroke="var(--color-primary)" fill="var(--color-primary)" />
            </aside>
            <main>
              <h2>{{ recommendation.title }}</h2>
            </main>
          </div>
        </template>
        <template #outer>
          <div class="flex flex-col flex-gap">
            <Pin />
            <FileBarChart2 />
          </div>
        </template>
      </Recommendations>
    </Default>
  </section>
</template>
<script setup lang="ts">
import { FileBarChart2, Pin, Star } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import { applyRecommendation } from '@/api/services/RTE'
import context from '@/assets/json/context_rte.json'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

import Default from '../Common/Assistant/Default.vue'
import Recommendations from '../Common/Assistant/Recommendations.vue'
import Event from './Assistant/Event.vue'

const route = useRoute()
const servicesStore = useServicesStore()

const card = ref<Card<'RTE'>>()
const tab = ref(0)

eventBus.on('assistant:selected', (selected) => {
  card.value = selected as Card<'RTE'>
  tab.value = 1
})

eventBus.on('assistant:tab', (index) => {
  tab.value = index
  switch (index) {
    case 2:
      servicesStore.getRecommendation(context)
  }
})

function onSelection(selected: any) {
  sendTrace({
    data: {},
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendation(selected.actions[0])
  tab.value = 0
}
</script>
