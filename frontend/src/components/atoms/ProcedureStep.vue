<template>
  <div
    ref="step"
    class="procedure-step"
    :state="task.state"
    @click="task.state === 'doing' && eventBus.emit('assistant:procedure:checked', task)">
    <div class="timeline">
      <div class="line top"></div>
      <div class="circle"></div>
      <div class="line bottom"></div>
    </div>
    <div class="step">[{{ task.taskIndex }}]&nbsp;{{ task.taskText }}</div>
  </div>
  <slot name="footer">
    <Button
      v-if="!'LAND ASAP'.localeCompare(task.taskText.toUpperCase()) && task.state === 'doing'"
      @click="eventBus.emit('assistant:tab', 2), eventBus.emit('tabs:selected', 0)">
      {{ $t('assistant.plan') }}
    </Button>
  </slot>
</template>
<script setup lang="ts" generic="E extends Entity">
import { ref, watch } from 'vue'

import eventBus from '@/plugins/eventBus'
import type { Entity } from '@/types/entities'
import type { Step } from '@/types/procedure'

import Button from './Button.vue'

const props = defineProps<{
  task: Step<E>
}>()

const step = ref<HTMLDivElement>()

watch(
  () => props.task.state,
  (value: (typeof props.task)['state']) => {
    if (value === 'doing') step.value?.scrollIntoView({ behavior: 'smooth' })
  }
)
</script>
<style lang="scss">
.procedure-step {
  scroll-snap-align: start;
  display: flex;
  margin-left: var(--spacing-2);
  cursor: not-allowed;
  * {
    transition: var(--duration);
  }
  &[state='done'] {
    .line {
      background: var(--color-primary);
    }

    .circle {
      background: var(--color-primary);
      border: 2px solid var(--color-background);
    }
  }

  &[state='doing'] {
    cursor: pointer;
    .line.top {
      background: var(--color-primary);
    }

    .circle {
      background: var(--color-background);
      border: 2px solid var(--color-primary);
    }
    .step {
      color: var(--color-primary);
    }
  }

  .step {
    padding: calc(var(--spacing-1) / 2) var(--spacing-1);
  }

  .timeline {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .line {
    width: 4px;
    flex: 1;
    background: #c6c6c6;
    border-radius: 9px;
    margin: -2px 0;
  }

  .circle {
    width: 17px;
    height: 17px;
    border-radius: 99px;
    background: var(--color-background);
    border: 2px solid var(--color-grey-600);
    box-sizing: border-box;
    z-index: 100;
  }
}
</style>
