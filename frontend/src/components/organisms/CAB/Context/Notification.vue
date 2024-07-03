<template>
  <div
    v-if="shown"
    class="cab-context-notification"
    :class="{ expanded }"
    :style="{
      'border-color': card
        ? `var(--color-${criticalityToColor(card.data.criticality)})`
        : `var(--color-${color})`
    }">
    <Button
      :icon="$t(`cab.context.notification.expanded.${expanded}`)"
      style="float: right"
      @click="expanded = !expanded">
      <Minimize2 v-if="expanded"></Minimize2>
      <Maximize2 v-else></Maximize2>
    </Button>
    <main v-if="expanded">
      <h1>
        <slot name="title">
          <template v-if="card">
            {{ format(card.startDate, 'p') }}: {{ card.titleTranslated }}
          </template>
        </slot>
      </h1>

      <slot>
        <template v-if="card">{{ card.summaryTranslated }}</template>
      </slot>
    </main>
  </div>
</template>
<script setup lang="ts">
import { Maximize2, Minimize2 } from 'lucide-vue-next'
import { ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import { format } from '@/plugins/date'
import type { Card } from '@/types/cards'
import { criticalityToColor } from '@/utils/utils'

defineProps<{
  card?: Card
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
  top?: number
  right?: number
  bottom?: number
  left?: number
  shown: boolean
}>()

const expanded = ref(true)
</script>
<style lang="scss">
.cab-context-notification {
  opacity: 1;
  border: 4px solid;
  position: absolute;
  top: calc(v-bind(top) * var(--unit));
  right: calc(v-bind(right) * var(--unit));
  left: calc(v-bind(left) * var(--unit));
  bottom: calc(v-bind(bottom) * var(--unit));
  background: var(--color-background);
  border-radius: var(--radius-medium);
  padding: var(--spacing-2);
  animation: appear var(--duration);
  &.expanded {
    width: calc(var(--unit) * 42);
  }
}

@keyframes appear {
  from {
    opacity: 0;
  }
}
</style>
