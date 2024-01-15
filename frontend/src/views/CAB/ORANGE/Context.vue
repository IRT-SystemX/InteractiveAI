<template>
  <Context v-model="activeTab" :tabs="[$t('cab.tab.graph')]">
    <Graph v-if="activeTab === 0" :data="servicesStore.d3Correlations" />
  </Context>
  <div id="graph-tooltip">
    <div v-for="datum of tooltipData" :key="datum[0]" class="flex flex-center-v">
      <SVG
        :src="`icons/kpi/${datum[0]}`"
        fill="var(--color-primary)"
        :width="16"
        class="mr-1"></SVG>
      {{ $t('kpi.' + datum[0]) }} à {{ Math.round(datum[1]) }}%
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import SVG from '@/components/atoms/SVG.vue'
import Graph from '@/components/organisms/Graph.vue'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'

import Context from '../Common/Context.vue'

const activeTab = ref(0)
const servicesStore = useServicesStore()
const tooltipData = ref<any | undefined>(['test'])

eventBus.on('graph:showTooltip', (node) => {
  tooltipData.value = node
})
</script>
<style lang="scss">
#graph-tooltip {
  z-index: 1000;
  position: absolute;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: 0.75em;
  border: 1px solid var(--color-grey-600);
  padding: calc(var(--unit) / 2);
  border-radius: var(--radius-medium);
  pointer-events: none;
}
</style>
