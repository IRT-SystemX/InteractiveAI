<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.timeline') }}</h1>
    <Timeline
      v-slot="{ card }"
      :now="servicesStore.context('PowerGrid') && new Date(servicesStore.context('PowerGrid')!.date)"
      :start="-30"
      :end="210"
      entity="PowerGrid">
      <Zap
        v-if="card.severity === 'ALARM'"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :color="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :height="16" />
      <SVG
        v-else
        src="/img/icons/toolbox.svg"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :width="16"></SVG>
    </Timeline>
  </section>
</template>
<script setup lang="ts">
import { Zap } from 'lucide-vue-next'

import SVG from '@/components/atoms/SVG.vue'
import Timeline from '@/components/organisms/Timeline.vue'
import { useServicesStore } from '@/stores/services'
import { criticalityToColor } from '@/utils/utils'

const servicesStore = useServicesStore()
</script>
