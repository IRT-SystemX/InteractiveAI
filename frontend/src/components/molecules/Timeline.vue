<template>
  <div
    class="cab-timeline-top"
    :style="{ 'grid-template-columns': style['grid-template-columns'] }">
    <div
      v-for="card of cards"
      :key="card.id"
      class="cab-timeline-event"
      :style="{
        'grid-column': `${minmax(
          differenceInMinutes(new Date(card.startDate), window.start) + 2,
          window.length + 1,
          2
        )} / ${minmax(
          differenceInMinutes(card.endDate ? new Date(card.endDate) : new Date(), window.start) + 2,
          window.length + 1,
          2
        )}`
      }">
      <div class="cab-timeline-event-icon">
        <slot :card="card"></slot>
      </div>
    </div>
    <div class="cab-timeline-border"></div>
    <div
      class="cab-timeline-now"
      :style="{ 'grid-column': `${Math.abs(start) + 2} / ${Math.abs(start) + 4} ` }">
      <div class="cab-timeline-time">
        {{ format(now, 'p') }}
      </div>
    </div>
  </div>
  <div v-if="cards.length" class="cab-timeline" :style="style">
    <div class="cab-timeline-now" :style="{ 'grid-column': `${Math.abs(start) + 2}` }"></div>
    <div
      v-for="(_, time) in end - start"
      :key="time"
      class="cab-timeline-hover"
      :style="{ 'grid-column': `${time + 2}` }">
      <div class="cab-timeline-hover-time">
        {{ format(addMinutes(now, start + time), 'p') }}
      </div>
    </div>
    <template v-for="(card, index) of cards" :key="card.id">
      <Notification
        :severity="card.severity"
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
          'grid-column': `${minmax(
            differenceInMinutes(new Date(card.startDate), window.start) + 2,
            window.length + 1,
            2
          )} / ${minmax(
            differenceInMinutes(card.endDate ? new Date(card.endDate) : new Date(), window.start) +
              2,
            window.length + 1,
            2
          )}`
        }"
        class="cab-timeline-event">
        <div class="cab-timeline-event-icon">
          <slot :card="card"></slot>
        </div>
        <div class="cab-timeline-event-line" :class="severityToColor(card.severity)"></div>
        <div class="cab-timeline-event-time">
          <div
            v-if="card.startDate && isAfter(new Date(card.startDate), window.start)"
            class="start">
            {{ format(new Date(card.startDate), 'p') }}
          </div>
          <div v-if="card.endDate && isBefore(new Date(card.endDate), window.end)" class="end">
            {{ format(new Date(card.endDate), 'p') }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts">
import { addMinutes, differenceInMinutes, isAfter, isBefore } from 'date-fns'
import { computed, ref } from 'vue'

import { format } from '@/plugins/date'
import type { Card } from '@/types/cards'
import { minmax, repeatEvery, severityToColor } from '@/utils/utils'

import Notification from './Notification.vue'

const props = defineProps<{ start: number; end: number; cards: Card[] }>()

const now = ref(new Date())
const window = computed(() => ({
  start: addMinutes(now.value, props.start),
  end: addMinutes(now.value, props.end),
  length: props.end - props.start
}))
const style = computed(() => ({
  'grid-template-columns': `[cards-start] 304px [events-start] repeat(${window.value.length}, 1fr) [events-end]`,
  'grid-template-rows': `[events-start] ${
    props.cards.length ? `repeat(${props.cards.length}, 40px) [events-end]` : ''
  }`
}))

repeatEvery(() => {
  now.value = new Date()
}, 60 * 1000)
</script>
<style lang="scss" scoped>
.cab-timeline {
  display: grid;
  row-gap: var(--spacing-1);
  overflow-y: auto;
  scrollbar-gutter: stable;
  scroll-snap-type: y mandatory;
  height: 100%;

  &-top {
    display: grid;
    height: calc(var(--unit) * 2);
    // Because of scrollbar
    // TODO
    overflow: visible;
    scrollbar-gutter: stable;
    grid-template-rows: 1fr;
    > * {
      grid-row: events-start / events-end;
    }
    .cab-timeline-event {
      margin-bottom: calc(var(--unit) / 2);
    }
  }

  &-border {
    border-bottom: 2px solid var(--color-grey-400);
    grid-column: events-start / events-end;
  }

  &-now {
    grid-row: events-start / events-end;
    border-left: 2px solid var(--color-grey-400);
    position: relative;
  }

  &-time {
    position: absolute;
    transform: translateX(-50%);
    bottom: 0;
    padding-bottom: var(--spacing-2);
    width: max-content;
    &:after {
      content: '';
      position: absolute;
      left: -2px;
      bottom: 0;
      right: 0;
      margin: 0 auto;
      width: 0;
      height: 0;
      border-top: 16px solid var(--color-grey-400);
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
    }
  }

  &-hover {
    grid-row: events-start / events-end;
    z-index: 1;
    opacity: 0;
    cursor: cell;

    &:hover {
      background: color-mix(in srgb, var(--color-primary) 50%, #fff0);
      opacity: 1;
    }

    &-time {
      position: fixed;
      right: var(--spacing-4);
      background: var(--color-primary);
      border-radius: var(--radius-small);
      color: var(--color-text-inverted);
      font-size: 0.75rem;
      pointer-events: none;
      text-align: center;
      width: calc(var(--unit) * 5);
      width: max-content;
    }
  }

  &-card {
    grid-column: cards-start;
    margin-right: var(--spacing-1);
    scroll-snap-align: start;
  }

  &-line {
    grid-column: events-start / events-end;
    border-top: 2px dashed var(--color-grey-300);
    align-self: center;
  }

  &-event {
    align-self: center;

    &-icon {
      margin-left: calc(var(--spacing-1) * -1);
      height: 0;
      width: 0;
      bottom: 18px;
      position: relative;
    }

    &-time {
      font-size: 0.75rem;
      position: relative;

      .start,
      .end {
        position: absolute;
        background: var(--color-background);
        color: var(--color-grey-600);
        border-radius: var(--radius-small);
        padding: 0 calc(var(--unit) / 2);
        width: max-content;
      }
      .start {
        left: calc(var(--spacing-4) * -1);
      }
      .end {
        right: calc(var(--spacing-4) * -1);
      }
    }
    &-line {
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
}
</style>
