<template>
  <div
    class="cab-timeline-row"
    :class="{ active: appStore._card?.id === card.id }"
    :style="{
      gridTemplateColumns: `[cards-start] 304px [events-start] repeat(${window.length}, 1fr) [events-end]`
    }"
    @click="selected(card)">
    <div class="flex" style="scroll-snap-align: end">
      <CornerDownRight v-if="isChild" />
      <slot name="notification" :card>
        <Notification
          :criticality="card.data.criticality"
          class="cab-timeline-card flex-1"
          :class="{ active: appStore._card?.id === card.id }"
          :style="{
            color: card.read ? 'var(--color-grey-600)' : undefined
          }">
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
    <div
      :style="{
        'grid-column': `${clamp(
          differenceInMinutes(
            new Date(
              'creation_date' in card.data.metadata
                ? card.data.metadata.creation_date
                : card.startDate
            ),
            window.start
          ) + 2,
          window.length + 1,
          2
        )}`
      }"
      class="cab-timeline-event">
      <div class="cab-timeline-event-top">
        <slot :card></slot>
      </div>
      <div class="cab-timeline-event-bottom">
        {{
          format(
            new Date(
              'creation_date' in card.data.metadata
                ? card.data.metadata.creation_date
                : card.startDate
            ),
            'p'
          )
        }}
      </div>
    </div>
    <div
      :style="{
        'grid-column': `${clamp(
          differenceInMinutes(new Date(card.startDate), window.start) + 2,
          window.length + 1,
          2
        )} / ${clamp(
          differenceInMinutes(card.endDate ? new Date(card.endDate) : window.end, window.start) + 2,
          window.length + 1,
          2
        )}`
      }"
      class="cab-timeline-event">
      <div class="cab-timeline-event-top"></div>
      <div
        class="cab-timeline-event-middle"
        :class="criticalityToColor(card.data.criticality)"></div>
      <div class="cab-timeline-event-bottom w-100">
        <div v-if="card.startDate && isAfter(new Date(card.startDate), window.start)" class="start">
          {{ format(new Date(card.startDate), 'p') }}
        </div>
        <div
          v-if="
            card.endDate &&
            card.startDate !== card.endDate &&
            isBefore(new Date(card.endDate), window.end)
          "
          class="end">
          {{ format(new Date(card.endDate), 'p') }}
        </div>
      </div>
    </div>
    <div
      v-for="(event, eventIndex) of events.filter(
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
      <div class="cab-timeline-event-top">
        <template v-if="'name' in event">
          <span class="text-stroke">
            {{ format(new Date(event.startDate), 'p') }}
          </span>
          <MapPin v-if="eventIndex !== [card, ...events].length - 1" :size="16"></MapPin>
          <Flag v-else :size="16"></Flag>
          <span v-if="event.startDate !== event.endDate" class="text-stroke">
            {{ format(new Date(event.endDate), 'p') }}
          </span>
        </template>
        <slot v-else :card></slot>
      </div>
      <div
        class="cab-timeline-event-middle"
        :class="'name' in event ? '' : criticalityToColor(card.data.criticality)"></div>
      <div class="cab-timeline-event-bottom">
        <div class="text-stroke">
          {{ event.name }}
        </div>
      </div>
    </div>
  </div>
  <TreeNode
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
  </TreeNode>
</template>
<script setup lang="ts" generic="E extends Entity">
import { differenceInMinutes, isAfter, isBefore } from 'date-fns'
import { CornerDownRight, Flag, MapPin } from 'lucide-vue-next'
import { computed } from 'vue'

import Notification from '@/components/molecules/Notification.vue'
import { format } from '@/plugins/date'
import { useAppStore } from '@/stores/app'
import { useCardsStore } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { clamp, criticalityToColor } from '@/utils/utils'

export type eventFnType<E extends Entity = Entity> = (
  card: Card<E>
) => { id: string; startDate: number; endDate: number; name: string }[]

const props = withDefaults(
  defineProps<{
    now: Date
    card: Card<E>
    eventFn?: eventFnType<E>
    window: { start: Date; end: Date; length: number }
    index: number
    isChild: boolean
  }>(),
  {
    eventFn: undefined
  }
)

const cardsStore = useCardsStore()
const appStore = useAppStore()

const children = computed(() =>
  cardsStore
    .cards(props.card.entityRecipients[0])
    .filter((card) => card.data.parent_event_id === props.card.processInstanceId)
)
const events = computed(() =>
  typeof props.eventFn === 'function' ? props.eventFn(props.card) : []
)

function selected(card: Card<E>) {
  card.read = true
  appStore._card = card
}
</script>
<style lang="scss">
.cab-timeline-event {
  height: 100%;
  align-self: center;
  display: flex;
  flex-direction: column;
  &.error {
    color: var(--color-error);
  }
  &.warning {
    color: var(--color-warning);
  }
  &.success {
    color: var(--color-success);
  }
  &.primary {
    color: var(--color-primary);
  }

  .max {
    width: max-content;
  }

  .start {
    justify-self: start;
  }
  .end {
    justify-self: end;
  }
  &:has(.cab-timeline-event-middle) .cab-timeline-event-top,
  &:has(.cab-timeline-event-middle) .cab-timeline-event-bottom {
    padding: calc(var(--unit) / 2) 0;
  }

  &-top,
  &-bottom {
    font-size: 0.75rem;
    flex: 1;
    width: max-content;
    padding: var(--unit) 0;
    display: flex;
    justify-content: space-between;
  }
  &-top {
    align-items: flex-end;
  }

  &-middle {
    opacity: 0.6;
    height: 8px;
    border-radius: var(--radius-circular);

    &.error {
      background: var(--color-error);
    }
    &.warning {
      background: var(--color-warning);
    }
    &.success {
      background: var(--color-success);
    }
    &.primary {
      background: var(--color-primary);
    }
  }
}
.cab-timeline-row {
  display: grid;
  grid-column: cards-start / event-end;
  border-radius: var(--radius-medium);
  cursor: pointer;
  transition: var(--duration);

  > * {
    grid-row: 1;
    min-width: 0;
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
