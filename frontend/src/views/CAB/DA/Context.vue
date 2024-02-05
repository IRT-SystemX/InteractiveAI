<template>
  <Context
    v-model="tab"
    :tabs="[$t('cab.tab.map'), $t('cab.tab.synoptic'), $t('cab.tab.dependencies')]">
    <Map v-if="tab === 0"></Map>
    <Synoptic
      v-if="tab === 1"
      v-model:tab="synopticTab"
      :faulty="faulty"
      @update:tab="synopticTab = $event"></Synoptic>
    <div v-if="tab === 2">2</div>
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Map from '@/components/organisms/Map.vue'
import eventBus from '@/plugins/eventBus'
import { useMapStore } from '@/stores/components/map'
import { useServicesStore } from '@/stores/services'

import Context from '../Common/Context.vue'
import Synoptic, { type Tab } from './Context/Synoptic.vue'

const { t } = useI18n()
const servicesStore = useServicesStore()
const mapStore = useMapStore()

const tab = ref(0)
const contextPID = ref(0)
const synopticTab = ref<Tab>('ENG')
const faulty = ref(false)

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('DA', (context: any) => {
    mapStore.addContextWaypoint({
      lat: context.Latitude,
      lng: context.Longitude,
      id: t('map.context')
    })
  })
})

onUnmounted(() => {
  clearInterval(contextPID.value)
})

eventBus.on('assistant:selected:DA', () => {
  tab.value = 1
  faulty.value = true
  synopticTab.value = 'ECS'
})

eventBus.on('tabs:selected', (value) => {
  tab.value = value
})
</script>
