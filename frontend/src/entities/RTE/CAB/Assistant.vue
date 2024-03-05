<template>
  <section class="cab-panel">
    <Default>
      <Event v-if="tab === 1 && card" :card="card" :primary-action="primaryAction">
        {{ card.titleTranslated }}
      </Event>
      <Recommendations
        v-if="tab === 2"
        :recommendations="servicesStore.recommendations('RTE')"
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
import Default from '@/components/organisms/CAB/Assistant.vue'
import Event from '@/components/organisms/CAB/Assistant/Event.vue'
import Recommendations from '@/components/organisms/CAB/Assistant/Recommendations.vue'
import { applyRecommendation } from '@/entities/RTE/api'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { Trace } from '@/types/services'

import context from '../assets/context.json'

const route = useRoute()
const servicesStore = useServicesStore()

const card = ref<Card<'RTE'>>()
const tab = ref(0)

eventBus.on('assistant:selected:RTE', (selected) => {
  card.value = selected
  tab.value = 1
})

eventBus.on('assistant:tab', (index) => {
  tab.value = index
  switch (index) {
    case 2:
      servicesStore.getRecommendation(context as any)
  }
})

function onSelection(selected: any) {
  sendTrace({
    data: selected,
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendation(selected.actions[0])
  tab.value = 0
}

function primaryAction() {
  sendTrace({
    data: {} as Trace['data'],
    use_case: route.params.entity as Entity,
    step: 'ASKFORHELP'
  })
  eventBus.emit('assistant:tab', 2)
}
</script>
