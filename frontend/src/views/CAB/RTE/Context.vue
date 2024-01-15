<template>
  <Context v-model="activeTab" :tabs="[$t('cab.tab.context')]">
    <img
      v-if="activeTab === 0"
      :src="`data:image/png;base64, ${topology}`"
      class="cab-context-topology" />
  </Context>
</template>
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { useServicesStore } from '@/stores/services'

import Context from '../Common/Context.vue'

const activeTab = ref(0)

const servicesStore = useServicesStore()

const contextId = ref(0)

const topology = ref('')

onMounted(async () => {
  contextId.value = await servicesStore.getContext('RTE', (context: any) => {
    topology.value = context.topology
  })
})

onBeforeUnmount(() => {
  clearInterval(contextId.value)
})
</script>
<style lang="scss">
.cab-context-topology {
  max-width: 100%;
  max-height: 100%;
}
</style>
