<template>
  <Context v-model="tab" :tabs="[$t('cab.tab.context')]">
    <img
      v-if="tab === 0"
      :src="`data:image/png;base64, ${topology}`"
      class="cab-context-topology" />
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onBeforeUnmount, ref } from 'vue'

import { useServicesStore } from '@/stores/services'

import Context from '../Common/Context.vue'

const servicesStore = useServicesStore()

const tab = ref(0)
const contextPID = ref(0)
const topology = ref('')

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('RTE', (context: any) => {
    topology.value = context.topology
  })
})

onBeforeUnmount(() => {
  clearInterval(contextPID.value)
})
</script>
<style lang="scss">
.cab-context-topology {
  max-width: 100%;
  max-height: 100%;
}
</style>
