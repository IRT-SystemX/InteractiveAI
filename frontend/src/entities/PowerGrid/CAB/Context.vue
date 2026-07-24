<template>
  <Context :tabs="[$t('cab.tab.context')]">
    <template v-if="appStore.tab.context === 0">
      <ZoomImg
        v-if="context"
        class="cab-context-topology"
        zoom-type="drag"
        :src="`data:image/svg+xml;base64, ${context}`"
        :show-zoom-btns="true"
        :persist="true"
        :zoom-scale="5"
        :step="0.5" />
      <h1 v-else>{{ $t('cab.tab.nocontext') }}</h1>
    </template>
    <Notification
      :card="appStore.card('PowerGrid')"
      :shown="!!appStore.card('PowerGrid')"
      :top="1"
      :right="1"></Notification>
    <Notification
      :card="appStore.card('PowerGrid')"
      :shown="!!appStore.card('PowerGrid')"
      :top="1"
      :left="1">
      <template #title>KPIs</template>
      <b></b>
      <div v-for="(value, key) of appStore.card('PowerGrid')!.data.metadata.kpis" :key="key">
        <b>{{ $t(`PowerGrid.kpis.${key}`) }}</b>
        {{ isFinite(+value) ? (+value).toFixed(4) : value }}
      </div>
    </Notification>
    <Button
      v-if="appStore.card('PowerGrid')"
      icon="Current time frame"
      style="position: absolute; right: var(--spacing-1); bottom: var(--spacing-1)"
      @click="appStore._card = undefined">
      <TimerReset />
    </Button>
  </Context>
</template>
<script setup lang="ts">
import { TimerReset } from 'lucide-vue-next'
import { computed, onBeforeMount, onUnmounted, ref } from 'vue'
import { ZoomImg } from 'vue3-zoomer'

import Button from '@/components/atoms/Button.vue'
import Context from '@/components/organisms/CAB/Context.vue'
import Notification from '@/components/organisms/CAB/Context/Notification.vue'
import { useAppStore } from '@/stores/app'
import { useServicesStore } from '@/stores/services'

const servicesStore = useServicesStore()
const appStore = useAppStore()

const contextPID = ref(0)

const context = computed(
  () =>
    appStore.card('PowerGrid')?.data.metadata.event_context ||
    servicesStore.context('PowerGrid')?.data.topology
)

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext('PowerGrid')
})

onUnmounted(() => {
  clearInterval(contextPID.value)
})
</script>
<style lang="scss">
.cab-context-topology {
  max-width: calc(100% - 30px);
  max-height: calc(100% - 30px);
  width: 100%;
  height: 100%;
}
.cab-context-topology .vz-zoomimg-img {
  width: inherit;
  height: inherit;
}
</style>
