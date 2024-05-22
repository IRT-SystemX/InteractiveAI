<template>
  <section class="cab-panel">
    <Default>
      <template #title>
        <template v-if="appStore.tab.assistant === 2">
          {{ $t('cab.assistant.recommendations') }}
        </template>
      </template>
      <Event
        v-if="appStore.tab.assistant === 1 && appStore.card('RTE')"
        :card="appStore.card('RTE')!"
        :primary-action="primaryAction"
        :secondary-action="() => {}">
        {{ appStore.card('RTE')!.titleTranslated }}
      </Event>
      <Recommendations
        v-if="appStore.tab.assistant === 2"
        v-model:recommendations="recommendations"
        :buttons="[$t('recommendations.button1'), $t('recommendations.button2')]"
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
        <template #footer="{ selected }">
          <div class="scrollable-y">
            <table v-if="recommendations.length">
              <thead>
                <tr>
                  <th>KPI</th>
                  <th
                    v-for="(recommendation, index) of recommendations"
                    :key="recommendation.title"
                    :class="{ active: selected?.title === recommendation.title }">
                    P{{ index }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(_, key) of recommendations[0].kpis" :key="key">
                  <td>{{ $t(`rte.kpis.${key}`) }}</td>
                  <td
                    v-for="recommendation of recommendations"
                    :key="recommendation.title"
                    :class="{ active: selected?.title === recommendation.title }">
                    {{
                      isFinite(recommendation.kpis?.[key])
                        ? recommendation.kpis?.[key].toFixed(4)
                        : recommendation.kpis?.[key]
                    }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </Recommendations>
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import Button from '@/components/atoms/Button.vue'
import Default from '@/components/organisms/CAB/Assistant.vue'
import Event from '@/components/organisms/CAB/Assistant/Event.vue'
import Recommendations from '@/components/organisms/CAB/Assistant/Recommendations.vue'
import { applyRecommendation } from '@/entities/RTE/api'
import { useAppStore } from '@/stores/app'
import { useServicesStore } from '@/stores/services'
import type { Entity } from '@/types/entities'
import type { Recommendation } from '@/types/services'

const route = useRoute()
const servicesStore = useServicesStore()
const appStore = useAppStore()

const recommendations = ref<Recommendation<'RTE'>[]>([])

watch(
  () => appStore._card,
  () => {
    appStore.tab.assistant = 1
  }
)
watch(
  () => appStore.tab.assistant,
  async (index) => {
    switch (index) {
      case 2:
        if (!appStore.card('DA')) break
        await servicesStore.getRecommendation(appStore.card('RTE')!.data!)
        recommendations.value = servicesStore.recommendations('RTE')
    }
  }
)

function onSelection(selected: any) {
  sendTrace({
    data: selected,
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendation(selected.actions[0])
  appStore.tab.assistant = 0
}

function primaryAction() {
  sendTrace({
    data: { id: appStore.card('RTE')!.id },
    use_case: route.params.entity as Entity,
    step: 'ASKFORHELP'
  })
  appStore.tab.assistant = 2
}
</script>
<style scoped lang="scss">
table {
  overflow: auto;
  width: 100%;
  border-collapse: collapse;
  tr > * {
    border-right: 2px solid var(--color-background);
    text-align: center;
  }
  thead tr,
  tbody tr:nth-child(even) {
    background-color: var(--color-grey-200);
  }

  .active {
    background-color: var(--color-grey-300);
  }
}
</style>
