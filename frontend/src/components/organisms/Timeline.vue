<template>
  <div class="cab-timeline" :style>
    <!--Header section-->
    <div style="grid-row: 1; grid-column: 1"></div>
    <!--Bottom border-->
    <div class="cab-timeline-top cab-timeline-top-border"></div>
    <!--Current time and cursor-->
    <div
      class="cab-timeline-top cab-timeline-top-now"
      :style="{ 'grid-column': `${Math.abs(start) + 2} / ${Math.abs(start) + 4} ` }">
      <div class="cab-timeline-time">
        {{ format(now, 'p') }}
      </div>
    </div>
    <!--Cards section-->
    <!--Current time vertical line
    <div class="cab-timeline-now" :style="{ 'grid-column': `${Math.abs(start) + 2}` }"></div>-->
    <!--Time steps for hover informations
    <div
      v-for="(_, time) in end - start"
      :key="time"
      class="cab-timeline-hover"
      :style="{ 'grid-column': `${time + 2}` }">
      <div class="cab-timeline-hover-time">
        {{ format(addMinutes(now, start + time), 'p') }}
      </div>
    </div>-->
    <!--Cards-->
    <div
      v-if="Object.keys(cards).length"
      :style="{
        gridTemplateColumns: style.gridTemplateColumns,
        gridColumn: 'cards-start / event-end',
        rowGap: '8px',
        display: 'grid'
      }">
      <template
        v-for="key of Object.keys(cards).sort((a, b) => {
          return (
            CriticalityArray.indexOf(maxCriticality('ND', cards[b])) -
            CriticalityArray.indexOf(maxCriticality('ND', cards[a]))
          )
        })"
        :key>
        <Notification v-if="key !== '_DEFAULT'" :criticality="maxCriticality('ND', cards[key])">
          <div class="flex flex-center-y flex-gap">
            <ChevronDown />
            <header class="flex flex-1">
              <b class="flex-1">Application {{ +/\d+/.exec(key)![0] }}</b>
              <aside>{{ $t('cab.notifications.group', cards[key].length) }}</aside>
            </header>
          </div>
        </Notification>
        <TimelineTreeNode
          v-for="(c, index) of cards[key]"
          :key="c.id"
          :is-child="key !== '_DEFAULT'"
          :card="c"
          :window
          :index
          :now
          :event-fn="eventFn"
          :children="c.children">
          <template #notification="{ card }">
            <slot name="notification" :card></slot>
          </template>
          <slot :card="c"></slot>
          <template #title="{ card }">
            <slot name="title" :card></slot>
          </template>
        </TimelineTreeNode>
      </template>
    </div>
  </div>
</template>
<script setup lang="ts" generic="T extends Entity">
import { addMinutes } from 'date-fns'
import { ChevronDown } from 'lucide-vue-next'
import groupBy from 'object.groupby'
import { computed, ref } from 'vue'

import Notification from '@/components/molecules/Notification.vue'
import TimelineTreeNode, { type eventFnType } from '@/components/molecules/TimelineTreeNode.vue'
import { format } from '@/plugins/date'
import { useCardsStore } from '@/stores/cards'
import { type Card, CriticalityArray } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { maxCriticality, repeatEvery } from '@/utils/utils'

const props = withDefaults(
  defineProps<{
    now?: Date
    start: number
    end: number
    groupFn?: (card: Card<T>) => string
    eventFn?: eventFnType<T>
    entity: T
  }>(),
  {
    now: undefined,
    groupFn: () => '_DEFAULT',
    eventFn: () => []
  }
)

const cardsStore = useCardsStore()

const window = computed(() => ({
  start: addMinutes(now.value, props.start),
  end: addMinutes(now.value, props.end),
  length: props.end - props.start
}))
const now = computed(() => props.now || localNow.value)
const style = computed(() => ({
  gridTemplateColumns: `[cards-start] 304px [events-start] repeat(${window.value.length}, 1fr) [events-end]`,
  gridAutoRows: `40px`
}))
const cards = computed(() =>
  groupBy(
    cardsStore.parseTree(
      [...cardsStore.cards(props.entity)].sort(
        (a, b) =>
          CriticalityArray.indexOf(b.data.criticality) -
          CriticalityArray.indexOf(a.data.criticality)
      )
    ),
    props.groupFn
  )
)

const localNow = ref(new Date())

if (!props.now)
  repeatEvery(() => {
    localNow.value = new Date()
  }, 60 * 1000)
</script>
<style lang="scss">
.cab-timeline {
  display: grid;
  row-gap: var(--spacing-1);
  overflow: hidden auto;
  scrollbar-gutter: stable;
  scroll-snap-type: y mandatory;
  height: 100%;

  &-top {
    position: sticky;
    top: 0;
    grid-row: 1;
    z-index: 100;
    &-now {
      z-index: 101;
    }
    &-border {
      border-bottom: 2px solid var(--color-grey-400);
      grid-column: events-start / events-end;
      background: var(--color-background);
    }
    &-event {
      display: flex;
      align-items: flex-end;
      padding-bottom: var(--unit);
      min-width: 0;
      overflow: visible;
      svg {
        position: absolute;
      }
    }
  }

  &-now {
    border-left: 2px solid var(--color-grey-400);
  }

  &-time {
    position: sticky;
    transform: translateX(-50%);
    top: 0;
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
    scroll-snap-align: end;
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
