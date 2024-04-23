<template>
  <Context v-model="tab" :tabs="[$t('cab.tab.context')]">
    <template v-if="tab === 0">
      <img
        v-if="topology"
        style="user-drag: none"
        :src="`data:image/png;base64, ${topology}`"
        class="cab-context-topology" />
      <h1 v-else>Pas de contexte</h1>
    </template>
    <Notification :card></Notification>
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
const previousContext = ref('')
const topology = ref('')
const card = ref<Card<'RTE'> | undefined>(undefined)

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('RTE', (context, data) => {
    if (!previousContext.value) previousContext.value = data.id_context
    if (previousContext.value !== data.id_context) topology.value = context.data.topology
  })
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
