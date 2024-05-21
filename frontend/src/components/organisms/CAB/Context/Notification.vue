<template>
  <div
    v-if="card"
    class="cab-context-notification"
    :class="{ expanded }"
    :style="{
      'border-color': `var(--color-${criticalityToColor(card.data.criticality)})`
    }">
    <Button icon style="float: right" @click="expanded = !expanded">
      <Minimize2 v-if="expanded"></Minimize2>
      <Maximize2 v-else></Maximize2>
    </Button>
    <main v-if="expanded">
      <h1>
        <slot name="title">{{ format(card.startDate, 'p') }}: {{ card.titleTranslated }}</slot>
      </h1>

      <slot>{{ card.summaryTranslated }}</slot>
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

defineProps<{ card?: Card; top?: number; right?: number; bottom?: number; left?: number }>()

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
