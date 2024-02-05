<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline v-slot="{ card }" :cards="cardsStore.cards('SNCF')" :start="-30" :end="210">
      <SVG
        src="icons/warning_hex"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        :width="16"></SVG>
    </Timeline>
  </section>
</template>
<script setup lang="ts">
import SVG from '@/components/atoms/SVG.vue'
import Timeline from '@/components/molecules/Timeline.vue'
import { useCardsStore } from '@/stores/cards'
import { severityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()
</script>
