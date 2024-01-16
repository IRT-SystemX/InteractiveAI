<template>
  <Context
    v-model="activeTab"
    :tabs="[
      $t('cab.tab.incident'),
      $t('cab.tab.equipment'),
      $t('cab.tab.passengers'),
      $t('cab.tab.map')
    ]">
    <div v-if="activeTab === 0">0</div>
    <div v-if="activeTab === 1">1</div>
    <div v-if="activeTab === 2">2</div>
    <Map
      v-if="activeTab === 3"
      :tile-layers="[
        'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
        'https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png'
      ]" />
  </Context>
</template>
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

import Map from '@/components/organisms/Map.vue'
import { useCardsStore } from '@/stores/cards'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'
import type { Severity } from '@/types/cards'

import Context from '../Common/Context.vue'

const activeTab = ref(0)

const servicesStore = useServicesStore()
const mapStore = useMapStore()
const cardsStore = useCardsStore()

const contextId = ref(0)

onMounted(async () => {
  contextId.value = await servicesStore.getContext('SNCF', (context: any) => {
    for (const train of context.trains)
      mapStore.addContextWaypoint({
        lat: train.latitude,
        lng: train.longitude,
        id: train.id_train,
        options: {
          severity: cardsStore.cards.reduce((acc: Severity | undefined, curr) => {
            if (curr.data?.metadata.id_train === train.id_train) return curr.severity
            return acc
          }, undefined)
        }
      })
  })
})

onBeforeUnmount(() => {
  clearInterval(contextId.value)
})
</script>
@/stores/components/map