<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline
      v-slot="{ card }"
      :cards="cardsStore.cards('RTE')"
      :start="-30"
      :end="210"
      entity="RTE">
      <Zap
        v-if="card.severity === 'ALARM'"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :color="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :height="16" />
      <SVG
        v-else
        src="icons/toolbox"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :width="16"></SVG>
    </Timeline>
  </section>
</template>
<script setup lang="ts">
import { Zap } from 'lucide-vue-next'

import SVG from '@/components/atoms/SVG.vue'
import Timeline from '@/components/organisms/Timeline.vue'
import { useCardsStore } from '@/stores/cards'
import { criticalityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()
</script>
