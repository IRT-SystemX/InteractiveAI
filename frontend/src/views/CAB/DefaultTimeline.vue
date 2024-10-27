<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline v-slot="{ card }" :start="-120" :end="120" entity="RTE">
      <SVG
        src="/img/icons/warning_hex.svg"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :width="16"></SVG>
    </Timeline>
  </section>
</template>
<script setup lang="ts">
import SVG from '@/components/atoms/SVG.vue'
import Timeline from '@/components/organisms/Timeline.vue'
import { criticalityToColor } from '@/utils/utils'
</script>
