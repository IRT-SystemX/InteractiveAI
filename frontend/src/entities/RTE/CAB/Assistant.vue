<template>
  <section class="cab-panel">
    <Default>
      <template #title>
        <template v-if="tab === 2">{{ $t('cab.assistant.recommendations') }}</template>
      </template>
      <Event v-if="tab === 1 && card" :card :primary-action="primaryAction">
        {{ card.titleTranslated }}
      </Event>
      <Recommendations
        v-if="tab === 2"
        :buttons="[$t('recommendations.button1'), $t('recommendations.button2')]"
        :recommendations="servicesStore.recommendations('RTE')"
        @selected="onSelection">
        <template #default="{ recommendation }">
          <div class="flex">
            <main>
              <h2>{{ recommendation.title }}</h2>
            </main>
          </div>
        </template>
        <template #button>
          <Button color="secondary">{{ $t('recommendations.button.secondary') }}</Button>
        </template>
      </Recommendations>
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import Button from '@/components/atoms/Button.vue'
import Default from '@/components/organisms/CAB/Assistant.vue'
import Event from '@/components/organisms/CAB/Assistant/Event.vue'
import Recommendations from '@/components/organisms/CAB/Assistant/Recommendations.vue'
import { applyRecommendation } from '@/entities/RTE/api'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

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
      servicesStore.getRecommendation(card.value?.data.metadata!)
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
    data: card.value!.id,
    use_case: route.params.entity as Entity,
    step: 'ASKFORHELP'
  })
  eventBus.emit('assistant:tab', 2)
}
</script>
