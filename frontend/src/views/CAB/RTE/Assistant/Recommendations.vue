<template>
  <main class="cab-parries">
    <div class="flex flex-wrap flex-gap">
      <Settings />
      <Button>Coût</Button>
      <Button>LTTD > 2h</Button>
    </div>
    <CardVue
      v-for="(recommendation, index) of servicesStore.recommendations"
      :key="recommendation.title"
      orientation="right"
      class="correlation-card"
      :class="{ selected: selectedRecommendation === index }"
      @click="selectedRecommendation = index">
      <div class="flex">
        <aside class="flex flex-center mr-1">
          <Star stroke="var(--color-primary)" fill="var(--color-primary)" />
        </aside>
        <main>
          <h2>{{ recommendation.title }}</h2>
        </main>
      </div>
      <template #outer>
        <div class="flex flex-col flex-gap">
          <Pin />
          <FileBarChart2 />
        </div>
      </template>
    </CardVue>
    <Button v-if="selectedRecommendation !== undefined" class="self-end" @click="applyParry">
      Appliquer
    </Button>
    <div v-if="selectedRecommendation !== undefined">
      <h2>Description parade</h2>
      {{ servicesStore.recommendations[selectedRecommendation].description }}
    </div>
  </main>
</template>
<script setup lang="ts">
import { FileBarChart2, Pin, Settings, Star } from 'lucide-vue-next'
import { onMounted } from 'vue'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { applyRecommendationRTE, sendTrace } from '@/api/services'
import context from '@/assets/json/context_rte.json'
import Button from '@/components/atoms/Button.vue'
import CardVue from '@/components/atoms/Card.vue'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { Metadata } from '@/types/entities/RTE'

const selectedRecommendation = ref<number>()
const route = useRoute()

const servicesStore = useServicesStore()

defineProps<{ card: Card<Metadata> }>()

function applyParry() {
  sendTrace({
    data: {},
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendationRTE(servicesStore.recommendations[selectedRecommendation.value!].actions[0])
  eventBus.emit('assistant:tab', 0)
}

onMounted(async () => {
  await servicesStore.getRecommendation(context)
})
</script>
<style lang="scss">
.cab-parries {
  display: flex;
  flex-direction: column;
  height: 0;

  .correlation-card {
    scroll-snap-align: start;
    .cab-card-outer {
      width: 0;
      color: #fff0;
      max-width: fit-content;
      transition: var(--duration);

      .lucide:hover {
        fill: var(--color-background);
      }
    }
    &.selected .cab-card-inner {
      background: var(--color-grey-200);
    }
    &:hover .cab-card-outer,
    &.selected .cab-card-outer {
      color: #fff;
      width: 40px;
    }
    .cab-card-inner {
      display: flex;
      justify-content: space-between;
    }
  }
}
</style>
