<template>
  <Context
    v-model="tab"
    :tabs="[$t('cab.tab.map'), $t('cab.tab.synoptic'), $t('cab.tab.dependencies')]">
    <Map v-if="tab === 0"></Map>
    <div v-if="tab === 1">1</div>
    <div v-if="tab === 2">2</div>
  </Context>
</template>
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

import Map from '@/components/organisms/Map.vue'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'

import Context from '../Common/Context.vue'

const tab = ref(0)

const servicesStore = useServicesStore()
const mapStore = useMapStore()

const contextId = ref(0)

onMounted(async () => {
  contextId.value = await servicesStore.getContext('DA', (context: any) => {
    mapStore.addContextWaypoint({ lat: context.Latitude, lng: context.Longitude, id: 'Plane' })
  })
})

onBeforeUnmount(() => {
  clearInterval(contextId.value)
})
</script>
<style lang="scss"></style>
@/stores/components/map