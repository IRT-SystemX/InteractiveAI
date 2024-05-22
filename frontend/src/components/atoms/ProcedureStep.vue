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
    <div
      class="step"
      :style="{ gridColumn: cab ? 3 : 1, gridRow: 1, textAlign: cab ? 'left' : 'right' }">
      [{{ task.taskIndex }}]&nbsp;{{ task.taskText }}
    </div>
  </div>
  <slot name="footer">
    <Button
      v-if="!'LAND ASAP'.localeCompare(task.taskText.toUpperCase()) && task.state === 'doing'"
      @click="
        () => {
          appStore.tab.assistant = 2
          appStore.tab.context = 0
        }
      ">
      {{ $t('assistant.plan') }}
    </Button>
  </slot>
</template>
<script setup lang="ts" generic="E extends Entity">
import { ref, watch } from 'vue'

import eventBus from '@/plugins/eventBus'
import { useAppStore } from '@/stores/app'
import type { Entity } from '@/types/entities'
import type { Step } from '@/types/procedure'

import Button from './Button.vue'

const props = defineProps<{
  task: Step<E>
  cab?: boolean
}>()

const appStore = useAppStore()

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
  scroll-margin: calc(var(--unit) * 5);
  display: grid;
  grid-template-columns: calc(50% - var(--unit)) calc(var(--unit) * 2) calc(50% - var(--unit));
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
      border-color: var(--color-background);
    }
  }

  &[state='doing'] {
    cursor: pointer;
    .line.top {
      background: var(--color-primary);
    }

    .circle {
      background: var(--color-background);
      border-color: var(--color-primary);
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
    grid-column: 2;
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
    z-index: 99;
  }
}
</style>
