<template>
  <section class="cab-panel">
    <Default>
      <Procedure v-if="tab === 1" />
      <Recommendations
        v-if="tab === 2"
        :recommendations="servicesStore.recommendations"
        :buttons="[
          $t('recommendations.button1'),
          $t('recommendations.button2'),
          $t('recommendations.button3')
        ]"
        @selected="onSelection"></Recommendations>
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import eventBus from '@/plugins/eventBus'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'

import Default from '../Common/Assistant/Default.vue'
import Recommendations from '../Common/Assistant/Recommendations.vue'
import Procedure from './Assistant/Procedure.vue'

const servicesStore = useServicesStore()
const mapStore = useMapStore()

const tab = ref(0)

eventBus.on('assistant:selected', async () => {
  tab.value = 1
})

eventBus.on('assistant:tab', async (index) => {
  tab.value = index
  switch (index) {
    case 2:
      await servicesStore.getRecommendation({})
      for (const recommendation of servicesStore.recommendations)
        for (const action of recommendation.actions) {
          for (const { latitude, longitude, wpid } of action.waypoints)
            mapStore.addWaypoint({ lat: latitude, lng: longitude, id: wpid })
          mapStore.addWaypoint({
            lat: action.airport_destination.latitude,
            lng: action.airport_destination.longitude,
            id: action.airport_destination.apname
          })
          mapStore.addPolyline({
            id: recommendation.title,
            waypoints: [
              ...action.waypoints.map((waypoint: any) => ({
                lat: waypoint.latitude,
                lng: waypoint.longitude,
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
})

function onSelection(recommendation: any) {
  mapStore.resetPolylines()
  mapStore.resetWaypoints()
  for (const action of recommendation.actions) {
    for (const { latitude, longitude, wpid } of action.waypoints)
      mapStore.addWaypoint({ lat: latitude, lng: longitude, id: wpid })
    mapStore.addWaypoint({
      lat: action.airport_destination.latitude,
      lng: action.airport_destination.longitude,
      id: action.airport_destination.apname
    })

    mapStore.addPolyline({
      id: action.title,
      waypoints: [
        ...action.waypoints.map((waypoint: any) => ({
          lat: waypoint.latitude,
          lng: waypoint.longitude,
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
  tab.value = 0
}
</script>
<style lang="scss" scoped>
.cab-assistant main {
  overflow: auto;
  scroll-snap-type: y mandatory;
}
</style>
