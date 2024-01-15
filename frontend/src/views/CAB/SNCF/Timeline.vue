<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline :cards="cardsStore.cards" :start="-30" :end="210"></Timeline>
  </section>
</template>
<script setup lang="ts">
import Timeline from '@/components/molecules/Timeline.vue'
import { useCardsStore } from '@/stores/cards'

const cardsStore = useCardsStore()
</script>
<style lang="scss"></style>
