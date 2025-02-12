<template>
  <section class="cab-panel">
    <Default>
      <template #title>
        <template v-if="appStore.tab.assistant === 2">
          {{ $t('cab.assistant.recommendations') }}
        </template>
        <template v-if="appStore.tab.assistant === 3">{{ $t('cab.assistant.procedure') }}</template>
      </template>
      <Event
        v-if="appStore.tab.assistant === 1 && appStore.card('Railway')"
        :card="appStore.card('Railway')!"
        :primary-action="
          appStore.card('Railway')?.data.metadata.event_type === 'INFRASTRUCTURE' &&
          !cardsStore
            .cards('Railway')
            .find((card) => card.data.parent_event_id === appStore.card('Railway')?.processInstanceId)
            ? null
            : primaryAction
        ">
        <template #event>
          <i18n-t
            scope="global"
            :keypath="
              appStore.card('Railway')!.data.metadata.event_type === 'PASSENGER'
                ? 'event.text.passenger'
                : appStore.card('Railway')?.data.metadata.event_type === 'INFRASTRUCTURE' &&
                    !cardsStore
                      .cards('Railway')
                      .find(
                        (card) =>
                          card.data.parent_event_id === appStore.card('Railway')?.processInstanceId
                      )
                  ? 'event.text.infrastructure_childless'
                  : 'event.text'
            ">
            <template #event>
              <strong
                :style="{
                  color: `var(--color-${criticalityToColor(appStore.card('Railway')!.data.criticality)}`
                }">
                {{ appStore.card('Railway')!.titleTranslated }}
              </strong>
            </template>
          </i18n-t>
        </template>
        <template #button-primary>
          <template v-if="appStore.card('Railway')!.data.metadata.event_type === 'PASSENGER'">
            {{ $t('event.button.primary.passenger') }}
          </template>
        </template>
        <template v-if="appStore.card('Railway')!.data.metadata.event_type === 'PASSENGER'" #tooltip>
          {{ $t('event.tooltip.primary.passenger') }}
        </template>
      </Event>
      <Recommendations
        v-if="appStore.tab.assistant === 2 && appStore.card('Railway')"
        v-model:recommendations="recommendations"
        :buttons="[
          $t('recommendations.button1'),
          $t('recommendations.button2'),
          $t('recommendations.button3'),
          $t('recommendations.button4')
        ]"
        @selected="onSelection">
        <template #default="{ recommendation }">
          <div class="flex">
            <main>
              <h2>{{ recommendation.title }}</h2>
            </main>
          </div>
        </template>
        <template #modal="{ selected }">
          <i18n-t scope="global" keypath="recommendations.modal">
            <template #recommendation>
              <strong style="color: var(--color-primary)">
                {{ selected?.title }}
              </strong>
            </template>
          </i18n-t>
        </template>
        <template #button>
          <Button color="secondary">{{ $t('recommendations.button.secondary') }}</Button>
        </template>
      </Recommendations>
      <Procedure
        v-if="appStore.tab.assistant === 3 && procedure && appStore.card('Railway')"
        :procedure />
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import { getProcedure } from '@/api/services'
import Button from '@/components/atoms/Button.vue'
import Default from '@/components/organisms/CAB/Assistant.vue'
import Event from '@/components/organisms/CAB/Assistant/Event.vue'
import Procedure from '@/components/organisms/CAB/Assistant/Procedure.vue'
import Recommendations from '@/components/organisms/CAB/Assistant/Recommendations.vue'
import { applyRecommendation } from '@/entities/Railway/api'
import { useAppStore } from '@/stores/app'
import { useCardsStore } from '@/stores/cards'
import { useServicesStore } from '@/stores/services'
import type { Entity } from '@/types/entities'
import type { Recommendation } from '@/types/services'
import { criticalityToColor, getRootCard } from '@/utils/utils'

const route = useRoute()
const cardsStore = useCardsStore()
const servicesStore = useServicesStore()
const appStore = useAppStore()

const procedure = ref()
const recommendations = ref<Recommendation<'Railway'>[]>([])

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
        await servicesStore.getRecommendation(appStore.card('Railway')!)
        recommendations.value = servicesStore.recommendations('Railway')
        break
      case 3:
        procedure.value = (await getProcedure('PASSENGER')).data.procedure
        procedure.value[0].tasks[0].state = 'doing'
    }
  }
)

function onSelection(recommendation: any) {
  sendTrace({
    data: recommendation,
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendation({
    ...recommendation.actions[0],
    event_id: getRootCard(appStore.card('Railway')!).processInstanceId
  })
  appStore.tab.assistant = 0
}

function primaryAction() {
  sendTrace({
    data: { id: appStore.card('Railway')!.id },
    use_case: route.params.entity as Entity,
    step: 'ASKFORHELP'
  })
  if (appStore.card('Railway')?.data.metadata.event_type === 'PASSENGER') {
    appStore.tab.assistant = 3
  } else appStore.tab.assistant = 2
}
</script>
