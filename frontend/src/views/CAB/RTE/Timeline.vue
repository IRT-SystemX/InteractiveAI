<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline v-slot="{ card }" :cards="cardsStore.cards" :start="-30" :end="210">
      <Zap
        v-if="card.severity === 'ALARM'"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        :color="`var(--color-${severityToColor(card.severity)})`"
        :height="16" />
      <SVG
        v-else
        src="icons/toolbox"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        :width="16"></SVG>
    </Timeline>
  </section>
</template>
<script setup lang="ts">
import { Zap } from 'lucide-vue-next'

import SVG from '@/components/atoms/SVG.vue'
import Timeline from '@/components/molecules/Timeline.vue'
import { useCardsStore } from '@/composables/cardsStoreWrapper'
import { severityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()
</script>
