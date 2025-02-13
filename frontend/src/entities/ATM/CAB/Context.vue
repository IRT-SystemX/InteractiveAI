<template>
  <Context :tabs="[$t('cab.tab.map')]">
    <Map v-if="appStore.tab.context === 0" />
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import Context from '@/components/organisms/CAB/Context.vue'
import Map from '@/components/organisms/Map.vue'
import type { System } from '@/entities/ATM/types'
import { useAppStore } from '@/stores/app'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'


const { t, locale } = useI18n()
const servicesStore = useServicesStore()
const mapStore = useMapStore()
const appStore = useAppStore()

const contextPID = ref(0)
const faulty = ref(false)


onBeforeMount(async () => {
  locale.value = `en-ATM`
  contextPID.value = await servicesStore.getContext('ATM', (context) => {
    mapStore.addContextWaypoint({
      lat: context.data.Latitude,
      lng: context.data.Longitude,
      id: t('map.context')
    })
    const waypoints = [
      ...(context.data.wpList
        ? context.data.wpList.map(({ wplat, wplon, wpid }) => ({
            id: wpid,
            lat: wplat,
            lng: wplon
          }))
        : []),
      ...(context.data.ApDest
        ? [
            {
              id: context.data.ApDest.apid,
              lat: context.data.ApDest.aplat,
              lng: context.data.ApDest.aplon,
              permanentTooltip: true
            }
          ]
        : [])
    ]
    mapStore.addPolyline({
      id: 'current_route',
      waypoints
    })
    mapStore.removeCategoryWaypoint('ROUTE')
    for (const waypoint of waypoints) mapStore.addWaypoint({ ...waypoint, category: 'ROUTE' })
  })
})

onUnmounted(() => {
  locale.value =
    window.navigator.language.split('-')[0] || import.meta.env.VITE_DEFAULT_LOCALE || 'en'
  clearInterval(contextPID.value)
})
</script>
