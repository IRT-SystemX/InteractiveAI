<template>
  <Notification
    :criticality="card.data.criticality"
    class="cab-timeline-card"
    :style="{ 'grid-row': index + 1 }">
    <template #title>
      {{ card.titleTranslated }}
    </template>
    <template #severity>
      <slot :card="card"></slot>
    </template>
  </Notification>
  <div class="cab-timeline-line" :style="{ 'grid-row': index + 1 }"></div>
  <div
    :style="{
      'grid-row': index + 1,
      'grid-column': `${clamp(
        differenceInMinutes(new Date(card.startDate), window.start) + 2,
        window.length + 1,
        2
      )} / ${clamp(
        differenceInMinutes(card.endDate ? new Date(card.endDate) : new Date(), window.start) + 2,
        window.length + 1,
        2
      )}`
    }"
    class="cab-timeline-event">
    <div class="cab-timeline-event-icon">
      <slot :card="card"></slot>
    </div>
    <div class="cab-timeline-event-line" :class="criticalityToColor(card.data.criticality)"></div>
    <div class="cab-timeline-event-time">
      <div v-if="card.startDate && isAfter(new Date(card.startDate), window.start)" class="start">
        {{ format(new Date(card.startDate), 'p') }}
      </div>
      <div v-if="card.endDate && isBefore(new Date(card.endDate), window.end)" class="end">
        {{ format(new Date(card.endDate), 'p') }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts" generic="T extends Entity">
import { differenceInMinutes, isAfter, isBefore } from 'date-fns'

import { format } from '@/plugins/date'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { clamp, criticalityToColor } from '@/utils/utils'

import Notification from '../molecules/Notification.vue'

defineProps<{
  card: Card<T>
  children: Card<T>[]
  window: { start: Date; end: Date; length: number }
  index: number
}>()
</script>
<style lang="scss">
.lucide {
  transition: var(--duration);
  &.rotate {
    transform: rotate(-90deg);
  }
}
</style>
