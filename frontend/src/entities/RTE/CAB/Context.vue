<template>
  <Context v-model="tab" :tabs="[$t('cab.tab.context')]">
    <template v-if="tab === 0">
      <img
        v-if="servicesStore.context('RTE')?.data.topology"
        style="user-drag: none"
        :src="`data:image/png;base64, ${servicesStore.context('RTE').data.topology}`"
        class="cab-context-topology" />
      <h1 v-else>Pas de contexte</h1>
    </template>
    <Notification :card :top="1" :right="1"></Notification>
    <Notification :card :top="1" :left="1">
      <template #title>KPIs</template>
      <b></b>
      <div v-for="(value, key) of card?.data.metadata.kpis" :key="key">
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
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'

const servicesStore = useServicesStore()

const tab = ref(0)
const contextPID = ref(0)
const card = ref<Card<'RTE'> | undefined>(undefined)

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('RTE')
})

eventBus.on('assistant:selected:RTE', (selected) => {
  card.value = selected
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
