<template>
  <div class="cab-timeline" :style>
    <!--Header section-->
    <div style="grid-row: 1; grid-column: 1; position: fixed" class="flex flex-gap">
      <Button
        icon="Previous time frame"
        @click="
          () => {
            _start -= window.length
            _end -= window.length
          }
        ">
        <ChevronLeft />
      </Button>
      <Button
        icon="Current time frame"
        @click="
          () => {
            _start = props.start
            _end = props.end
          }
        ">
        <TimerReset />
      </Button>
      <Button
        icon="Next time frame"
        @click="
          () => {
            _start += window.length
            _end += window.length
          }
        ">
        <ChevronRight />
      </Button>
    </div>
    <!--Bottom border-->
    <div class="cab-timeline-top cab-timeline-top-border"></div>
    <!--Hours-->
    <div
      v-for="marker of markers"
      :key="marker.getTime()"
      class="cab-timeline-top"
      :style="{ 'grid-column': `${differenceInMinutes(marker, window.start) + 2}` }">
      <div class="cab-timeline-time">
        {{ format(marker, isSameDay(marker, now) ? 'p' : 'Pp	') }}
      </div>
    </div>
    <!--Current time and cursor-->
    <div
      v-if="isWithinInterval(now, window)"
      class="cab-timeline-top cab-timeline-top-now"
      :style="{ 'grid-column': `${differenceInMinutes(now, window.start) + 2}` }">
      <div class="cab-timeline-time text-stroke">
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
            CRITICALITIES.indexOf(maxCriticality('ND', cards[b])) -
            CRITICALITIES.indexOf(maxCriticality('ND', cards[a]))
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
          :event-fn="eventFn">
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
<script setup lang="ts" generic="E extends Entity">
import {
  addMinutes,
  differenceInMinutes,
  eachHourOfInterval,
  isSameDay,
  isWithinInterval
} from 'date-fns'
import { ChevronDown, ChevronLeft, ChevronRight, TimerReset } from 'lucide-vue-next'
import groupBy from 'object.groupby'
import { computed, ref } from 'vue'

import Notification from '@/components/molecules/Notification.vue'
import { format } from '@/plugins/date'
import { useCardsStore } from '@/stores/cards'
import { type Card, CRITICALITIES } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { maxCriticality, repeatEvery } from '@/utils/utils'

import Button from '../atoms/Button.vue'
import TimelineTreeNode, { type eventFnType } from './Timeline/TreeNode.vue'

const props = withDefaults(
  defineProps<{
    now?: Date
    start: number
    end: number
    groupFn?: (card: Card<E>) => string
    eventFn?: eventFnType<E>
    entity: E
  }>(),
  {
    now: undefined,
    groupFn: () => '_DEFAULT',
    eventFn: () => []
  }
)

const cardsStore = useCardsStore()

const window = computed(() => ({
  start: addMinutes(now.value, _start.value),
  end: addMinutes(now.value, _end.value),
  length: props.end - props.start
}))
const markers = computed(() =>
  eachHourOfInterval({
    start: window.value.start,
    end: window.value.end
  }).filter((marker) => differenceInMinutes(marker, window.value.start) >= 0)
)
const now = computed(() => props.now || localNow.value)
const style = computed(() => ({
  gridTemplateColumns: `[cards-start] 304px [events-start] repeat(${window.value.length}, minmax(0, 1fr)) [events-end]`,
  gridAutoRows: `40px`
}))
const cards = computed(() =>
  groupBy(
    [...cardsStore.cards(props.entity)]
      .filter((c) => !c.data.parent_event_id)
      .sort(
        (a, b) =>
          CRITICALITIES.indexOf(b.data.criticality) - CRITICALITIES.indexOf(a.data.criticality)
      ),
    props.groupFn
  )
)

const _start = ref(props.start)
const _end = ref(props.end)
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
      .cab-timeline-time {
        color: var(--color-primary);
        font-weight: bold;
        &::after {
          border-top-color: var(--color-primary);
        }
      }
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
      border-left: 8px solid #fff0;
      border-right: 8px solid #fff0;
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
}
</style>
