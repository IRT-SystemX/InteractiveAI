<template>
  <Context
    :tabs="[
      $t('cab.tab.map')
    ]">
    <Map
      v-if="appStore.tab.context === 0"
      :tile-layers="[
  'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
  'https://{s}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png'
]"
 />
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onUnmounted, ref, watchEffect } from 'vue'

import Context from '@/components/organisms/CAB/Context.vue'
import Map from '@/components/organisms/Map.vue'
import { useAppStore } from '@/stores/app'
import { useCardsStore } from '@/stores/cards'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'
import type { Severity } from '@/types/cards'
import { criticalityToColor } from '@/utils/utils'

const servicesStore = useServicesStore()
const mapStore = useMapStore()
const cardsStore = useCardsStore()
const appStore = useAppStore()

const contextPID = ref(0)

watchEffect(() => {
  for (const train of cardsStore.cards('Railway'))
    if (train.data.metadata.latitude && train.data.metadata.longitude)
      mapStore.addWaypoint({
        id: train.data.metadata.event_type,
        lat: train.data.metadata.latitude,
        lng: train.data.metadata.longitude,
        category: 'EVENT',
        options: {
          stroke: true,
          radius: 8,
          color: `var(--color-${criticalityToColor(train.data.criticality)})`,
          fillColor: `var(--color-${criticalityToColor(train.data.criticality)})`,
          weight: 16,
          opacity: 0.5
        }
      })
})

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('Railway', (context) => {
    for (const train of context.data.trains)
      mapStore.addContextWaypoint({
        lat: train.latitude,
        lng: train.longitude,
        id: train.id_train,
        severity: cardsStore.cards('Railway').reduce((acc: Severity | undefined, curr) => {
          if (curr.data.metadata.id_train === train.id_train) return curr.severity
          return acc
        }, undefined)
      })
  })
})

onUnmounted(() => {
  clearInterval(contextPID.value)
})
</script>
