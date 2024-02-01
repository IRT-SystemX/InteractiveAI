<template>
  <section class="cab-panel">
    <Default>
      <Event v-if="tab === 1 && card" :card="card" />
      <Recommendations
        v-if="tab === 2"
        :recommendations="servicesStore.recommendations"
        :buttons="[
          $t('recommendations.button1'),
          $t('recommendations.button2'),
          $t('recommendations.button3'),
          $t('recommendations.button4')
        ]"
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
        <template #modal="{ selected }">
          <i18n-t scope="global" keypath="recommendations.modal">
            <template #recommendation>
              <strong style="color: var(--color-primary)">
                {{ selected.title }}
              </strong>
            </template>
            <template #train>
              <strong style="color: var(--color-primary)">
                {{ card?.data?.metadata.id_train }}
              </strong>
            </template>
          </i18n-t>
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
import { applyRecommendation } from '@/api/services/SNCF'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { Metadata } from '@/types/entities/SNCF'

import Default from '../Common/Assistant/Default.vue'
import Recommendations from '../Common/Assistant/Recommendations.vue'
import Event from './Assistant/Event.vue'

const route = useRoute()
const servicesStore = useServicesStore()

const card = ref<Card<Metadata>>()
const tab = ref(0)

eventBus.on('assistant:selected', (selected) => {
  card.value = selected
  tab.value = 1
})

eventBus.on('assistant:tab', (index) => {
  tab.value = index
  switch (index) {
    case 2:
      servicesStore.getRecommendation({})
  }
})

function onSelection(recommendation: any) {
  sendTrace({
    data: {},
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendation(recommendation.actions[0])
  eventBus.emit('assistant:tab', 0)
}
</script>
