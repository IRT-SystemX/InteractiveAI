<template>
  <Context
    v-model="tab"
    :tabs="[$t('cab.tab.map'), $t('cab.tab.synoptic'), $t('cab.tab.dependencies')]">
    <Map v-if="tab === 0"></Map>
    <Synoptic
      v-if="tab === 1"
      :tab="synopticTab"
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
<style lang="scss">
.btn-group-synoptic button {
  background-color: white;
  color: black;
  padding: 2px 24px;
  cursor: pointer;
  float: left;
}

.btn-group button:not(:last-child) {
  border-right: none;
}

.btn-group:after {
  content: '';
  clear: both;
  display: table;
}

.btn-group button:hover {
  background-color: #0085cc;
  color: white;
}
.btn-group-synoptic button:active,
.btn-group-synoptic button:hover,
.btn-group-synoptic button:focus,
.btn-group-synoptic-active {
  background-color: #9b9b9b !important;
}
.btn-group-synoptic button {
  background: none;
  background-color: #4b4b4b;
  color: white;
  border: none;
  font-weight: bold;
}
.btn-group-synoptic {
  display: inline-flex;
  background: none;
  color: white;
}
.btn-group button:active,
.btn-group button:focus,
.btn-group button:hover,
.btn-group-active {
  background-color: #9b9b9b !important;
  color: white;
  border-radius: 32px;
  font-weight: bold;
}

#synoptic_back {
  background-color: black;
  height: 340px;
  width: 91%;
  border-radius: 7px;
}
</style>
