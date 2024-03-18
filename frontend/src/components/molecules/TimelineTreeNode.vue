<template>
  <div
    class="cab-timeline-top cab-timeline-top-event"
    :style="{
      'grid-column': `${clamp(
        differenceInMinutes(new Date(card.startDate), window.start) + 2,
        window.length + 1,
        2
      )}`
    }">
    <slot :card="card"></slot>
  </div>
  <div class="cab-timeline-event" :style="grid">
    <div class="">
      <slot name="child-icon"></slot>
      <Notification :criticality="card.data.criticality" class="cab-timeline-card flex-1">
        <template #title>
          {{ card.titleTranslated }}
        </template>
        <template #severity>
          <slot :card="card"></slot>
        </template>
      </Notification>
    </div>
    <div class="cab-timeline-line"></div>
    <div
      v-if="!children"
      :style="{
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
  </div>
  <TimelineTreeNode
    v-for="(child, i) of children"
    :key="child.id"
    :window="window"
    :card="child"
    :grid="grid"
    :index="index + i + 1">
    <template #child-icon><CornerDownRight /></template>
    <slot :card="card"></slot>
  </TimelineTreeNode>
</template>
<script setup lang="ts" generic="T extends Entity">
import { differenceInMinutes, isAfter, isBefore } from 'date-fns'
import { CornerDownRight } from 'lucide-vue-next'

import { format } from '@/plugins/date'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { clamp, criticalityToColor } from '@/utils/utils'

import Notification from '../molecules/Notification.vue'

defineProps<{
  card: Card<T>
  children?: Card<T>[]
  window: { start: Date; end: Date; length: number }
  index: number
  grid: {
    'grid-template-columns': string
    'grid-auto-rows': string
  }
}>()
</script>
<style lang="scss">
.cab-timeline-event {
  display: grid;
  grid-column: cards-start / event-end;
}
.lucide {
  transition: var(--duration);
  &.rotate {
    transform: rotate(-90deg);
  }
}
</style>
