<template>
  <section class="cab-panel">
    <Default>
      <template #title>
        <template v-if="appStore.tab.assistant === 1">{{ $t('cab.assistant.procedure') }}</template>
        <template v-if="appStore.tab.assistant === 2">
          {{ $t('cab.assistant.recommendations') }}
        </template>
      </template>
      <Procedure
        v-if="appStore.tab.assistant === 1 && procedure && appStore.card('ATM')"
        :procedure />
      <Recommendations
        v-if="appStore.tab.assistant === 2 && appStore.card('ATM')"
        v-model:recommendations="recommendations"
        :buttons="[
          $t('recommendations.button1'),
          $t('recommendations.button2'),
          $t('recommendations.button3')
        ]"
        collapsed
        @hover="onHover"
        @selected="onSelection">
        <template #modal="{ selected }">
          <i18n-t scope="global" keypath="recommendations.modal">
            <template #destination>
              <strong style="color: var(--color-primary)">
                {{ selected?.actions[0].airport_destination.apcity }}
              </strong>
            </template>
          </i18n-t>
        </template>
      </Recommendations>
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

import { update } from '@/api/cards'
import { getProcedure } from '@/api/services'
import Default from '@/components/organisms/CAB/Assistant.vue'
import Procedure from '@/components/organisms/CAB/Assistant/Procedure.vue'
import Recommendations from '@/components/organisms/CAB/Assistant/Recommendations.vue'
import { useAppStore } from '@/stores/app'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'
import type { Recommendation } from '@/types/services'

import { applyRecommendation } from '../api'

const servicesStore = useServicesStore()
const mapStore = useMapStore()
const appStore = useAppStore()

const procedure = ref()
const recommendations = ref<Recommendation<'ATM'>[]>([])

watch(
  () => appStore._card,
  async () => {
    if (appStore.card('ATM')?.data.criticality !== 'HIGH') return
    appStore.tab.assistant = 1
    procedure.value = (
      await getProcedure(appStore.card('ATM')!.data.metadata.event_type)
    ).data.procedure
    procedure.value[0].tasks[0].state = 'doing'
  }
)

watch(
  procedure,
  (value) => {
    if (value.at(-1)?.tasks.at(-1)?.state === 'done')
      update({
        title: appStore.card('ATM')?.titleTranslated,
        description: appStore.card('ATM')?.summaryTranslated,
        data: appStore.card('ATM')?.data.metadata,
        use_case: 'ATM',
        criticality: 'ND'
      })
  },
  { deep: true }
)

watch(
  () => appStore.tab.assistant,
  async (index) => {
    switch (index) {
      case 1:
        if (!appStore.card('ATM')) break
        procedure.value = (
          await getProcedure(appStore.card('ATM')!.data.metadata.event_type)
        ).data.procedure
        procedure.value[0].tasks[0].state = 'doing'
        break
      case 2:
        if (!appStore.card('ATM')) break
        await servicesStore.getRecommendation(appStore.card('ATM')!)
        recommendations.value = servicesStore.recommendations('ATM')
        for (const recommendation of recommendations.value)
          for (const action of recommendation.actions) {
            for (const { wplat, wplon, wpid } of action.waypoints)
              mapStore.addWaypoint({
                lat: wplat,
                lng: wplon,
                id: wpid,
                category: 'RECOMMENDATION',
                options: { color: 'var(--color-primary)' }
              })
            mapStore.addWaypoint({
              lat: action.airport_destination.latitude,
              lng: action.airport_destination.longitude,
              id: action.airport_destination.apname,
              category: 'RECOMMENDATION',
              permanentTooltip: true,
              options: { color: 'var(--color-primary)' }
            })
            mapStore.addPolyline({
              id: recommendation.title,
              options: { color: 'var(--color-success)' },
              waypoints: [
                ...action.waypoints.map((waypoint: any) => ({
                  lat: waypoint.wplat,
                  lng: waypoint.wplon,
                  id: waypoint.wpid
                })),
                {
                  lat: action.airport_destination.latitude,
                  lng: action.airport_destination.longitude,
                  id: action.airport_destination.apname
                }
              ]
            })
          }
    }
  }
)

function onHover(hovered: Recommendation<'ATM'>) {
  for (const recommendation of recommendations.value)
    for (const action of recommendation.actions) {
      for (const { wplat, wplon, wpid } of action.waypoints)
        mapStore.addWaypoint({
          lat: wplat,
          lng: wplon,
          id: wpid,
          category: 'RECOMMENDATION',
          options: { color: 'var(--color-primary)' }
        })
      mapStore.addWaypoint({
        lat: action.airport_destination.latitude,
        lng: action.airport_destination.longitude,
        id: action.airport_destination.apname,
        category: 'RECOMMENDATION',
        permanentTooltip: true,
        options: { color: 'var(--color-primary)' }
      })
      mapStore.addPolyline({
        id: recommendation.title,
        options:
          hovered === recommendation ? { color: 'var(--color-primary)' } : { color: '#f3f3f3' },
        waypoints: [
          ...action.waypoints.map((waypoint: any) => ({
            lat: waypoint.wplat,
            lng: waypoint.wplon,
            id: waypoint.wpid
          })),
          {
            lat: action.airport_destination.latitude,
            lng: action.airport_destination.longitude,
            id: action.airport_destination.apname
          }
        ]
      })
    }
}

function onSelection(recommendation: Recommendation<'ATM'>) {
  applyRecommendation(recommendation.actions[0])
  mapStore.resetPolylines()
  mapStore.resetWaypoints()
  appStore.tab.assistant = 0
}
</script>
<style lang="scss" scoped>
.cab-assistant main {
  scroll-snap-type: y mandatory;
  scrollbar-gutter: stable both-edges;
}
</style>
