<template>
  <div class="procedure-block">
    <div class="procedure-block-title" :state>
      <slot name="block">{{ block.blockText }}</slot>
    </div>
  </div>
  <ProcedureStep
    v-for="task of block.tasks"
    :key="task.taskIndex"
    :task
    :cab="collaboration && block.enableAssistance"></ProcedureStep>
</template>
<script setup lang="ts" generic="E extends Entity">
import { computed } from 'vue'

import type { Entity } from '@/types/entities'
import type { Block } from '@/types/procedure'

import ProcedureStep from '../atoms/ProcedureStep.vue'

const props = defineProps<{ block: Block<Entity>; collaboration: boolean }>()

const state = computed(() => {
  if (props.block.tasks.every((task: any) => task.state === 'done')) return 'done'
  if (props.block.tasks.some((task: any) => task.state === 'doing')) return 'doing'
  return 'todo'
})
</script>
<style lang="scss">
.procedure-block {
  scroll-snap-align: start;
  display: flex;
  justify-content: center;
  background: red;
  width: 100%;
  align-self: center;
  position: sticky;
  z-index: 100;
  top: 0;
  height: calc(var(--unit) * 5);
  background: var(--color-background);

  &-title {
    transition: var(--duration);
    background: var(--color-grey-300);
    border-radius: 8px;
    width: fit-content;
    border: 2px solid var(--color-grey-300);
    color: #fff;
    padding: 8px;
    &[state='done'] {
      border-color: var(--color-primary);
    }

    &[state='doing'] {
      background: var(--color-primary);
      border-color: var(--color-primary);
    }
  }
}
</style>
