<template>
  <section class="cab-panel">
    <Default>
      <template #title>
        {{ $t('cab.assistant.recommendations') }}
      </template>
      <Recommendations
        v-if="appStore.tab.assistant === 1 && appStore.card('ATM')"
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
import Recommendations from '@/components/organisms/CAB/Assistant/Recommendations.vue'
import { useAppStore } from '@/stores/app'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'
import type { Recommendation } from '@/types/services'
import { applyRecommendation } from '../api'

const servicesStore = useServicesStore()
const mapStore = useMapStore()
const appStore = useAppStore()

const recommendations = ref<Recommendation<'ATM'>[]>([])

// Update the assistant tab watcher to handle recommendations with index 1.
watch(
  () => appStore.tab.assistant,
  async (index) => {
    if (index === 1) {
      if (!appStore.card('ATM')) return
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
  // Optionally, change the tab value to close the assistant.
  appStore.tab.assistant = 0
}
</script>

<style lang="scss" scoped>
.cab-assistant main {
  scroll-snap-type: y mandatory;
  scrollbar-gutter: stable both-edges;
}
</style>
