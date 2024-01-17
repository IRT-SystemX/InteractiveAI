<template>
  Flight plans recommendations
  <div class="flex flex-wrap">
    <Button>Cockpit maintenance</Button>
    <Button>Cost</Button>
    <Button>Accomodation</Button>
  </div>
  <Card
    v-for="recommendation of servicesStore.recommendations"
    :key="recommendation"
    orientation="right"
    @click="newRoute(recommendation)">
    <h1>{{ recommendation.title }}</h1>
  </Card>
</template>
<script setup lang="ts">
import { onBeforeMount } from 'vue'

import Button from '@/components/atoms/Button.vue'
import Card from '@/components/atoms/Card.vue'
import eventBus from '@/plugins/eventBus'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'

const mapStore = useMapStore()
const servicesStore = useServicesStore()

onBeforeMount(async () => {
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
})

function newRoute(recommendation: any) {
  mapStore.resetPolylines()
  mapStore.resetWaypoints()
  for (const action of recommendation.actions) {
    for (const { latitude, longitude, wpid } of action.waypoints)
      mapStore.addWaypoint({ lat: latitude, lng: longitude, id: wpid })
    mapStore.addWaypoint({
      lat: action.airport_destination.latitude,
      lng: action.airport_destination.longitude,
      id: action.airport_destination.apname + 'tp'
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
  eventBus.emit('assistant:tab', 0)
}
</script>
@/stores/components/map
