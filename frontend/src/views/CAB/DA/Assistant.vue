<template>
  <section class="cab-panel">
    <Default>
      <Recommendations
        v-if="servicesStore.recommendations.length"
        v-model="servicesStore.recommendations" />
      <Procedure v-else-if="procedure.length" :procedure="procedure" />
    </Default>
  </section>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'

import { getProcedure } from '@/api/services'
import eventBus from '@/plugins/eventBus'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'

import Default from '../Common/Assistant/Default.vue'
import Procedure from './Assistant/Procedure.vue'
import Recommendations from './Assistant/Recommendations.vue'

const procedure = ref<any[]>([])
const tasks = computed(() => procedure.value?.flatMap((block) => block.tasks))

const mapStore = useMapStore()
const servicesStore = useServicesStore()

eventBus.on('assistant:selectedCard', async (selectedCard) => {
  // TODO
  const { data } = await getProcedure()
  procedure.value = data.procedure
  procedure.value[0].tasks[0].state = 'doing'
})

eventBus.on('assistant:procedure:checked', (task) => {
  task.state = 'done'
  tasks.value[tasks.value?.findIndex((t) => t.taskIndex === task.taskIndex) + 1].state = 'doing'
})
eventBus.on('assistant:procedure:plan', async () => {
  await servicesStore.getRecommendation({})
  for (const recommendation of servicesStore.recommendations)
    for (const action of recommendation.actions) {
      for (const { latitude, longitude, wpid } of action.waypoints)
        mapStore.addWaypoint({ lat: latitude, lng: longitude, id: wpid })
      mapStore.addWaypoint({
        lat: action.airport_destination.latitude,
        lng: action.airport_destination.longitude,
        id: action.airport_destination.apname,
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
</script>
<style lang="scss" scoped>
.cab-assistant main {
  overflow: auto;
  scroll-snap-type: y mandatory;
}
</style>
@/stores/components/map