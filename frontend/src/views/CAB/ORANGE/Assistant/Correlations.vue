<template>
  <main class="cab-correlations">
    <h2>{{ $t('correlations.timestep') }}</h2>
    <div class="correlation-size">
      {{ $t('minute', 5) }}
      <input
        v-model="size"
        type="range"
        list="size"
        min="5"
        max="60"
        step="5"
        @change="getCorrelations()" />
      <datalist id="size">
        <option
          v-for="i of [5, 15, 30, 45, 60]"
          :key="i"
          :value="i"
          :label="$t('minute', i)"></option>
      </datalist>
      {{ $t('minute', 60) }}
    </div>
    <div class="color-primary text-center">{{ $t('minute', +size) }}</div>
    <Button class="self-center" @click="getCorrelations()">{{ $t('correlations.refresh') }}</Button>
    <div id="correlations">
      <CardVue
        v-for="correlation of graphStore.formattedData.slice(0, graphStore.shown)"
        :key="correlation[0]"
        orientation="right"
        class="correlation-card"
        @mouseenter="showLink(1, +/App_(\d+)/.exec(correlation[0])![1])"
        @click="focusLink(1, +/App_(\d+)/.exec(correlation[0])![1])"
        @mouseleave="hideLinks">
        {{ $t('correlations.app', { id: +/App_(\d+)/.exec(correlation[0])![1] }) }}
        <SVG
          :src="`icons/kpi/${/App_\d+\.KPI(|_composite)\.(.*)/.exec(correlation[0])![2]}`"
          :alt="$t(`kpi.${/App_\d+\.KPI(|_composite)\.(.*)/.exec(correlation[0])![2]}`)"
          :width="24"
          fill="var(--color-grey-600)"></SVG>
        <template #outer>{{ Math.round(correlation[1]) }}%</template>
      </CardVue>
    </div>
    <Button
      v-if="graphStore.shown < graphStore.formattedData.length"
      color="secondary"
      class="self-end"
      @click="more">
      {{ $t('button.more-results') }}
    </Button>
  </main>
</template>
<script setup lang="ts">
import { onMounted } from 'vue'
import { ref } from 'vue'
import { nextTick } from 'vue'

import { getCorrelations as getCorrelationsApi } from '@/api/services/ORANGE'
import Button from '@/components/atoms/Button.vue'
import CardVue from '@/components/atoms/Card.vue'
import SVG from '@/components/atoms/SVG.vue'
import { useGraphStore } from '@/stores/components/graph'
import type { Card } from '@/types/cards'
import type { Metadata } from '@/types/entities/ORANGE'
import { focusLink, hideLinks, showLink, zoomToNode } from '@/utils/d3'

const size = ref('5')

const graphStore = useGraphStore()

const props = defineProps<{ card: Card<Metadata> }>()

async function getCorrelations() {
  const app_id = /App_(\d+)/.exec(props.card.data?.metadata.id_app!)![1]
  const { data } = await getCorrelationsApi({
    size: +size.value / 5,
    app_id
  })
  graphStore.correlations = data[0].data
  graphStore.shown = 5
  graphStore.d3Correlations(+app_id)
  nextTick(() => zoomToNode(+app_id))
}

function more() {
  const app_id = +/App_(\d+)/.exec(props.card.data?.metadata.id_app!)![1]
  graphStore.shown += 5
  graphStore.d3Correlations()
  nextTick(() => zoomToNode(app_id))
}

onMounted(() => {
  getCorrelations()
})
</script>
<style lang="scss">
.cab-correlations {
  display: flex;
  flex-direction: column;
  height: 0;
  main {
    display: flex;
    flex: 1;
    flex-direction: column;
    overflow: hidden;
  }
  main > *:not(:last-child) {
    margin-bottom: 8px;
  }
  .correlation-size {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  #correlation-size {
    flex: 1;
    margin: 0 16px;
  }
  #correlations {
    display: flex;
    flex-direction: column;
    overflow: auto;
    gap: 4px;
    scroll-snap-type: y mandatory;
    flex: 1;
    .correlation-card {
      scroll-snap-align: start;
      .cab-card-inner {
        display: flex;
        justify-content: space-between;
      }
    }
  }
}
</style>
