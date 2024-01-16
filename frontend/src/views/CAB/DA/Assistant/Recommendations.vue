<template>
  Flight plans recommendations
  <div class="flex flex-wrap">
    <Button>Cockpit maintenance</Button>
    <Button>Cost</Button>
    <Button>Accomodation</Button>
  </div>
  <Card
    v-for="recommendation of modelValue"
    :key="recommendation"
    orientation="right"
    @click="newRoute(recommendation)">
    <h1>{{ recommendation.title }}</h1>
  </Card>
</template>
<script setup lang="ts">
import Button from '@/components/atoms/Button.vue'
import Card from '@/components/atoms/Card.vue'
import { useMapStore } from '@/stores/components/map'

const mapStore = useMapStore()

defineProps<{ modelValue: any[] }>()
const emit = defineEmits(['update:modelValue'])

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
  emit('update:modelValue', [])
}
</script>
@/stores/components/map