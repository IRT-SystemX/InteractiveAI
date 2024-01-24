<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline v-slot="{ card }" :cards="cardsStore.cards" :start="-120" :end="120">
      <CheckCircle2
        v-if="card.severity === 'INFORMATION'"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        stroke="var(--color-background)"
        :width="20" />
      <SVG
        v-else
        src="icons/warning_hex"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        :width="16"></SVG>
    </Timeline>
  </section>
</template>
<script setup lang="ts">
import { CheckCircle2 } from 'lucide-vue-next'

import SVG from '@/components/atoms/SVG.vue'
import Timeline from '@/components/molecules/Timeline.vue'
import { useCardsStore } from '@/stores/cards'
import { severityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()
</script>
