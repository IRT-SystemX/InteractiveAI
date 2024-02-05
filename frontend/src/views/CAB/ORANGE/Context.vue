<template>
  <Context v-model="tab" :tabs="[$t('cab.tab.graph')]">
    <Graph v-if="tab === 0" />
    <div id="graph-tooltip">
      <div v-for="datum of tooltipData" :key="datum[0]" class="flex flex-center-y">
        <SVG
          :src="`icons/kpi/${datum[0]}`"
          fill="var(--color-primary)"
          :width="16"
          class="mr-1"></SVG>
        {{ $t('kpi.' + datum[0]) }} {{ $t('to') }} {{ Math.round(datum[1]) }}%
      </div>
    </div>
  </Context>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import SVG from '@/components/atoms/SVG.vue'
import Graph from '@/components/organisms/Graph.vue'
import eventBus from '@/plugins/eventBus'
import type { Card } from '@/types/cards'

import Context from '../Common/Context.vue'

const card = ref<Card<'ORANGE'> | null>()
const tab = ref(0)
const tooltipData = ref<any | null>()

eventBus.on('graph:showTooltip', (node) => {
  tooltipData.value = node
})

eventBus.on('assistant:selected:ORANGE', (selected) => {
  card.value = selected
})
</script>
<style lang="scss">
#graph-tooltip {
  z-index: 1000;
  position: fixed;
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
