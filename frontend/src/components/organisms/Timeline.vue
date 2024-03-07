<template>
  <!--Header section-->
  <div
    class="cab-timeline-top"
    :style="{ 'grid-template-columns': style['grid-template-columns'] }">
    <!--Event icons-->
    <div
      v-for="card of cards"
      :key="card.id"
      class="cab-timeline-event"
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
      }">
      <div class="cab-timeline-event-icon">
        <slot :card="card"></slot>
      </div>
    </div>
    <!--Bottom border-->
    <div class="cab-timeline-border"></div>
    <!--Current time and cursor-->
    <div
      class="cab-timeline-now"
      :style="{ 'grid-column': `${Math.abs(start) + 2} / ${Math.abs(start) + 4} ` }">
      <div class="cab-timeline-time">
        {{ format(now, 'p') }}
      </div>
    </div>
  </div>
  <!--Cards section-->
  <div v-if="cards.length" class="cab-timeline" :style="style">
    <!--Current time vertical line-->
    <div class="cab-timeline-now" :style="{ 'grid-column': `${Math.abs(start) + 2}` }"></div>
    <!--Time steps for hover informations-->
    <div
      v-for="(_, time) in end - start"
      :key="time"
      class="cab-timeline-hover"
      :style="{ 'grid-column': `${time + 2}` }">
      <div class="cab-timeline-hover-time">
        {{ format(addMinutes(now, start + time), 'p') }}
      </div>
    </div>
    <!--Cards-->
    <TimelineTreeNode
      v-for="(card, index) of cards"
      :key="card.id"
      :card="card"
      :window="window"
      :index="index"
      :children="
        cards.filter((child) => child.data.parent_event_id === card.processInstanceId)
      "></TimelineTreeNode>
  </div>
</template>
<script setup lang="ts">
import { addMinutes, differenceInMinutes } from 'date-fns'
import { computed, ref } from 'vue'

import TimelineTreeNode from '@/components/molecules/TimelineTreeNode.vue'
import { format } from '@/plugins/date'
import type { Card } from '@/types/cards'
import { clamp, repeatEvery } from '@/utils/utils'

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
<style lang="scss">
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
    grid-template-rows: 1fr;
    // Because of scrollbar
    // TODO
    padding-right: 10px;
    overflow: visible;
    scrollbar-gutter: stable;
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
