<template>
  <main class="cab-parries">
    <div class="flex flex-wrap flex-gap">
      <Settings />
      <Button>{{ $t('recommendations.button1') }}</Button>
      <Button>{{ $t('recommendations.button2') }}</Button>
      <Button>{{ $t('recommendations.button3') }}</Button>
      <Button>{{ $t('recommendations.button4') }}</Button>
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
    <Button v-if="selectedRecommendation !== -1" class="self-end" @click="applyParry">
      {{ $t('button.apply') }}
    </Button>
    <div v-if="selectedRecommendation !== -1">
      <h2>{{ $t('recommendations.description') }}</h2>
      {{ servicesStore.recommendations[selectedRecommendation].description }}
    </div>
  </main>
</template>
<script setup lang="ts">
import { FileBarChart2, Pin, Settings, Star } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import { applyRecommendation } from '@/api/services/SNCF'
import context from '@/assets/json/context_rte.json'
import Button from '@/components/atoms/Button.vue'
import CardVue from '@/components/atoms/Card.vue'
import eventBus from '@/plugins/eventBus'
import { useServicesStore } from '@/stores/services'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { Metadata } from '@/types/entities/SNCF'

defineProps<{ card: Card<Metadata> }>()

const route = useRoute()
const servicesStore = useServicesStore()

const selectedRecommendation = ref<number>(-1)

servicesStore.getRecommendation(context)

function applyParry() {
  sendTrace({
    data: {},
    use_case: route.params.entity as Entity,
    step: 'AWARD'
  })
  applyRecommendation(servicesStore.recommendations[selectedRecommendation.value].actions[0])
  eventBus.emit('assistant:tab', 0)
}
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
