<template>
  <div
    class="cab-timeline-row"
    :class="{ active: appStore._card?.id === card.id }"
    :style="{
      gridTemplateColumns: `[cards-start] 304px [events-start] repeat(${window.length}, 1fr) [events-end]`
    }"
    @click="appStore._card = card">
    <div class="flex" style="scroll-snap-align: end">
      <CornerDownRight v-if="isChild" />
      <slot name="notification" :card>
        <Notification
          :criticality="card.data.criticality"
          class="cab-timeline-card flex-1"
          :class="{ active: appStore._card?.id === card.id }">
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
      v-for="(event, eventIndex) of [card, ...events].filter(
        (ev) =>
          (isAfter(new Date(ev.startDate), window.start) &&
            isBefore(new Date(ev.endDate ? ev.endDate : new Date()), window.end)) ||
          'data' in ev
      )"
      :key="event.id"
      :style="{
        'grid-column': `${clamp(
          differenceInMinutes(new Date(event.startDate), window.start) + 2,
          window.length + 1,
          2
        )} / ${clamp(
          differenceInMinutes(event.endDate ? new Date(event.endDate) : window.end, window.start) +
            2,
          window.length + 1,
          2
        )}`
      }"
      class="cab-timeline-event">
      <div class="cab-timeline-event-icon">
        <template v-if="'name' in event">
          <div
            class="text-stroke"
            style="
              width: max-content;
              position: absolute;
              transform: translate(-20%);
              font-size: 0.75em;
              display: flex;
              align-items: center;
            ">
            {{ format(new Date(event.startDate), 'p') }}
            <MapPin v-if="eventIndex !== [card, ...events].length - 1" :size="16"></MapPin>
            <Flag v-else :size="16"></Flag>
            <template v-if="event.startDate !== event.endDate">
              {{ format(new Date(event.endDate), 'p') }}
            </template>
          </div>
        </template>
        <slot v-else :card></slot>
      </div>
      <div
        v-if="!('name' in event) && events.length"
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
          class="text-stroke"
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
    :event-fn="eventFn"
    :now
    :window
    :card="child"
    :index="index + i + 1"
    :is-child="true">
    <template #notification><slot name="notification" :card="child"></slot></template>
    <slot :card="child"></slot>
  </TimelineTreeNode>
</template>
<script setup lang="ts" generic="T extends Entity">
import { differenceInMinutes, isAfter, isBefore } from 'date-fns'
import { CornerDownRight, Flag, MapPin } from 'lucide-vue-next'
import { computed } from 'vue'

import { format } from '@/plugins/date'
import { useAppStore } from '@/stores/app'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { clamp, criticalityToColor } from '@/utils/utils'

import Notification from '../molecules/Notification.vue'

export type eventFnType<T extends Entity = Entity> = (
  card: Card<T>
) => { id: string; startDate: number; endDate: number; name: string }[]

const props = withDefaults(
  defineProps<{
    now: Date
    card: Card<T>
    children?: Card<T>[]
    eventFn?: eventFnType<T>
    window: { start: Date; end: Date; length: number }
    index: number
    isChild: boolean
  }>(),
  {
    children: undefined,
    eventFn: undefined
  }
)

const appStore = useAppStore()

const events = computed(() =>
  typeof props.eventFn === 'function' ? props.eventFn(props.card) : []
)
</script>
<style lang="scss">
.cab-timeline-row {
  display: grid;
  grid-column: cards-start / event-end;
  border-radius: var(--radius-medium);
  cursor: pointer;
  transition: var(--duration);

  > * {
    grid-row: 1;
  }

  &:hover,
  &.active {
    background: var(--color-grey-200);
  }
  &:focus,
  &:focus-within,
  &:active {
    background: var(--color-grey-300);
  }
}
.lucide {
  transition: var(--duration);
  &.rotate {
    transform: rotate(-90deg);
  }
}
</style>
