<template>
  <Context v-model="tab" :tabs="[$t('cab.tab.graph')]">
    <Graph v-if="tab === 0" />
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
import { useGraphStore } from '@/stores/components/graph'
import type { Card } from '@/types/cards'
import type { Metadata } from '@/types/entities/ORANGE'

import Context from '../Common/Context.vue'

const card = ref<Card<Metadata> | null>()
const tab = ref(0)
const graphStore = useGraphStore()
const tooltipData = ref<any | null>()

eventBus.on('graph:showTooltip', (node) => {
  tooltipData.value = node
})

eventBus.on('assistant:selected', (selected) => {
  card.value = selected as Card<Metadata>
  graphStore.d3Correlations(+/App_(\d+)/.exec(card.value.data?.metadata.id_app!)![1])
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
