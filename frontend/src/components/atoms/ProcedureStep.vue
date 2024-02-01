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
  <Button
    v-if="!'LAND ASAP'.localeCompare(task.taskText.toUpperCase()) && task.state === 'doing'"
    @click="eventBus.emit('assistant:tab', 2), eventBus.emit('tabs:selected', 0)">
    {{ $t('assistant.plan') }}
  </Button>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'

import eventBus from '@/plugins/eventBus'

import Button from './Button.vue'

const props = defineProps<{ task: any }>()

const step = ref<HTMLDivElement | null>(null)

watch(
  () => props.task.state,
  (value: 'done' | 'doing' | undefined) => {
    if (value === 'doing') step.value?.scrollIntoView({ behavior: 'smooth' })
  }
)
</script>
<style lang="scss">
.procedure-step {
  scroll-snap-align: start;
  display: flex;
  margin-left: 16px;
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
    padding: 4px 8px;
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
