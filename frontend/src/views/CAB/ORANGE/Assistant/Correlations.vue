<template>
  <main class="cab-correlations">
    <h2>Pas de temps</h2>
    <div class="correlation-size">
      5min
      <input
        v-model="size"
        type="range"
        list="size"
        min="5"
        max="60"
        value="5"
        step="5"
        @change="getCorrelations()" />
      <datalist id="size">
        <option value="5" label="5min"></option>
        <option value="15" label="15min"></option>
        <option value="30" label="30min"></option>
        <option value="45" label="45min"></option>
        <option value="60" label="60min"></option>
      </datalist>
      60 min
    </div>
    <div class="color-primary text-center">{{ size }} min</div>
    <Button class="self-center" @click="getCorrelations()">Rafraîchir les résultats</Button>
    <h2 class="flex flex-center">
      <span class="color-primary">{{ graphStore.formattedData.length }}&nbsp;</span>
      corrélations trouvées
      <Info
        fill="var(--color-grey-600)"
        stroke="var(--color-background)"
        :width="20"
        class="ml-1" />
    </h2>
    <div id="correlations">
      <CardVue
        v-for="correlation of graphStore.formattedData.slice(0, graphStore.shown)"
        :key="correlation[0]"
        orientation="right"
        class="correlation-card"
        @mouseenter="showLink(1, +/App_(\d+)/.exec(correlation[0])![1])"
        @click="focusLink(1, +/App_(\d+)/.exec(correlation[0])![1])"
        @mouseleave="hideLinks">
        App {{ +/App_(\d+)/.exec(correlation[0])![1] }}
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
      + Résultats
    </Button>
  </main>
</template>
<script setup lang="ts">
import { Info } from 'lucide-vue-next'
import { onMounted } from 'vue'
import { ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import CardVue from '@/components/atoms/Card.vue'
import SVG from '@/components/atoms/SVG.vue'
import { useGraphStore } from '@/stores/components/graph'
import type { Card } from '@/types/cards'
import type { Metadata } from '@/types/entities/ORANGE'
import { focusLink, hideLinks, showLink } from '@/utils/d3'

const size = ref(5)

const graphStore = useGraphStore()

const props = defineProps<{ card: Card<Metadata> }>()

async function getCorrelations() {
  await graphStore.getCorrelations({
    size: size.value / 5,
    app_id: /App_(\d+)/.exec(props.card.data?.metadata.id_app!)![1]
  })
  graphStore.d3Correlations(+/App_(\d+)/.exec(props.card.data?.metadata.id_app!)![1])
}

function more() {
  graphStore.shown += 5
  graphStore.d3Correlations(+/App_(\d+)/.exec(props.card.data?.metadata.id_app!)![1])
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
