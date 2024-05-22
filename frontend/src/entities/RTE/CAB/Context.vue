<template>
  <Context v-model="appStore.tab.context" :tabs="[$t('cab.tab.context')]">
    <template v-if="appStore.tab.context === 0">
      <img
        v-if="servicesStore.context('RTE')?.data.topology"
        :src="`data:image/png;base64, ${servicesStore.context('RTE').data.topology}`"
        class="cab-context-topology" />
      <h1 v-else>Pas de contexte</h1>
    </template>
    <Notification :card="appStore.card('RTE')" :top="1" :right="1"></Notification>
    <Notification :card="appStore.card('RTE')" :top="1" :left="1">
      <template #title>KPIs</template>
      <b></b>
      <div v-for="(value, key) of appStore.card('RTE')!.data.metadata.kpis" :key="key">
        <b>{{ $t(`rte.kpis.${key}`) }}</b>
        {{ isFinite(+value) ? (+value).toFixed(4) : value }}
      </div>
    </Notification>
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onUnmounted, ref } from 'vue'

import Context from '@/components/organisms/CAB/Context.vue'
import Notification from '@/components/organisms/CAB/Context/Notification.vue'
import { useAppStore } from '@/stores/app'
import { useServicesStore } from '@/stores/services'

const servicesStore = useServicesStore()
const appStore = useAppStore()

const contextPID = ref(0)

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('RTE')
})

onUnmounted(() => {
  clearInterval(contextPID.value)
})
</script>
<style lang="scss">
.cab-context-topology {
  max-width: 100%;
  max-height: 100%;
}
</style>
