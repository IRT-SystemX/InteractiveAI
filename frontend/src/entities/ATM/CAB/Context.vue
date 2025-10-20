<template>
  <Context :tabs="[$t('cab.tab.map')]">
    <Map v-if="appStore.tab.context === 0" />
  </Context>
</template>

<script setup lang="ts">
import { onBeforeMount, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Context from '@/components/organisms/CAB/Context.vue'
import Map from '@/components/organisms/Map.vue'
import type { AirplaneContext, LegacyContext, ContextType } from '@/entities/ATM/types'
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
  contextPID.value = await servicesStore.getContext('ATM', (context: { data: ContextType }) => {
    // New context data: iterate over the airplanes array
    // 1-  Clear last tick's markers and ROUTE waypoints
    mapStore.removeCategoryWaypoint('ROUTE')
    // 2- add new markers and ROUTE waypoints
    if ('airplanes' in context.data) {
      context.data.airplanes.forEach((airplane: AirplaneContext) => {
        mapStore.addContextWaypoint({
          lat: airplane.Latitude,
          lng: airplane.Longitude,
          id: `plane-${airplane.id_plane}`
        })
        // build the route waypoints
        const waypoints = [
          ...(airplane.wpList
            ? airplane.wpList.map(({ wplat, wplon, wpid }) => ({
                id: wpid,
                lat: wplat,
                lng: wplon
              }))
            : []),
          ...(airplane.ApDest
            ? [
                {
                  id: airplane.ApDest.apid,
                  lat: airplane.ApDest.aplat,
                  lng: airplane.ApDest.aplon,
                  permanentTooltip: true
                }
              ]
            : [])
        ]
        // draw polyline for the plane
        mapStore.addPolyline({
          id: `current_route_plane-${airplane.id_plane}`,
          waypoints
        })
        // add each wp a ROUTE waypoint
        for (const waypoint of waypoints) {
          mapStore.addWaypoint({ ...waypoint, category: 'ROUTE' })
        }
      })
    } else {
      // Legacy context data handling
      const legacy = context.data as LegacyContext
      mapStore.addContextWaypoint({
        lat: legacy.Latitude,
        lng: legacy.Longitude,
        id: t('map.context')
      })
      const waypoints = [
        ...(legacy.wpList
          ? legacy.wpList.map(({ wplat, wplon, wpid }) => ({
              id: wpid,
              lat: wplat,
              lng: wplon
            }))
          : []),
        ...(legacy.ApDest
          ? [
              {
                id: legacy.ApDest.apid,
                lat: legacy.ApDest.aplat,
                lng: legacy.ApDest.aplon,
                permanentTooltip: true
              }
            ]
          : [])
      ]
      mapStore.addPolyline({
        id: 'current_route',
        waypoints
      })
      //mapStore.removeCategoryWaypoint('ROUTE')
      for (const waypoint of waypoints) {
        mapStore.addWaypoint({ ...waypoint, category: 'ROUTE' })
      }
    }
  })
})

onUnmounted(() => {
  locale.value =
    window.navigator.language.split('-')[0] || import.meta.env.VITE_DEFAULT_LOCALE || 'en'
  clearInterval(contextPID.value)
})
</script>
