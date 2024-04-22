<template>
  <div
    class="cab-timeline-row"
    :style="{
      gridTemplateColumns: `[cards-start] 304px [events-start] repeat(${window.length}, 1fr) [events-end]`
    }">
    <div class="flex">
      <slot name="notification" :card>
        <CornerDownRight v-if="isChild" />
        <Notification :criticality="card.data.criticality" class="cab-timeline-card flex-1">
          <template #title>
            <slot name="title" :card>{{ card.titleTranslated }}</slot>
          </template>
          <template #severity>
            <slot :card></slot>
          </template>
        </Notification>
      </slot>
    </div>
    <div class="cab-timeline-line"></div>
    <template v-if="!children?.length"></template>
    <div
      v-for="(event, eventIndex) of [card, ...eventFn(card)]"
      :key="event.id"
      :style="{
        'grid-column': `${clamp(
          differenceInMinutes(new Date(event.startDate), window.start) + 2,
          window.length + 1,
          2
        )} / ${clamp(
          differenceInMinutes(event.endDate ? new Date(event.endDate) : new Date(), window.start) +
            2,
          window.length + 1,
          2
        )}`
      }"
      class="cab-timeline-event">
      <div class="cab-timeline-event-icon">
        <template v-if="'name' in event">
          <div
            style="
              width: max-content;
              position: absolute;
              transform: translate(-20%);
              font-size: 0.75em;
              display: flex;
              align-items: center;
            ">
            {{ format(new Date(event.startDate), 'p') }}
            <MapPin v-if="eventIndex !== [card, ...eventFn(card)].length - 1" :size="16"></MapPin>
            <Flag v-else :size="16"></Flag>
            {{ format(new Date(event.endDate), 'p') }}
          </div>
        </template>
        <slot v-else :card></slot>
      </div>
      <div
        v-if="!('name' in event)"
        class="cab-timeline-event-icon"
        style="float: right; font-size: 0.75em; font-weight: bold"
        :class="criticalityToColor(event.data.criticality)">
        HRE
      </div>
      <div
        class="cab-timeline-event-line"
        :class="'name' in event ? '' : criticalityToColor(card.data.criticality)"></div>
      <div class="cab-timeline-event-time">
        <div
          v-if="
            event.startDate &&
            !('name' in event) &&
            isAfter(new Date(event.startDate), window.start)
          "
          class="start">
          {{ format(new Date(event.startDate), 'p') }}
        </div>
        <div
          v-if="'name' in event"
          style="position: absolute; width: max-content; left: 50%; transform: translate(-50%)">
          {{ event.name }}
        </div>
        <div
          v-if="
            event.endDate &&
            !('name' in event) &&
            event.startDate !== event.endDate &&
            isBefore(new Date(event.endDate), window.end)
          "
          class="end">
          {{ format(new Date(event.endDate), 'p') }}
        </div>
      </div>
    </div>
  </div>
  <TimelineTreeNode
    v-for="(child, i) of children"
    :key="child.id"
    :window
    :card="child"
    :index="index + i + 1"
    :is-child="true">
    <slot :card></slot>
  </TimelineTreeNode>
</template>
<script setup lang="ts" generic="T extends Entity">
import { differenceInMinutes, isAfter, isBefore } from 'date-fns'
import { CornerDownRight, Flag, MapPin } from 'lucide-vue-next'

import { format } from '@/plugins/date'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { clamp, criticalityToColor } from '@/utils/utils'

import Notification from '../molecules/Notification.vue'

withDefaults(
  defineProps<{
    card: Card<T>
    children?: Card<T>[]
    eventFn?: (card: Card<T>) => { id: string; startDate: number; endDate: number; name: string }[]
    window: { start: Date; end: Date; length: number }
    index: number
    isChild: boolean
  }>(),
  { children: undefined, eventFn: () => [] }
)
</script>
<style lang="scss">
.cab-timeline-row {
  display: grid;
  grid-column: cards-start / event-end;
  > * {
    grid-row: 1;
  }
}
.lucide {
  transition: var(--duration);
  &.rotate {
    transform: rotate(-90deg);
  }
}
</style>
