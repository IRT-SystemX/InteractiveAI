<template>
  <div class="procedure-block" :state>
    <slot name="block">{{ block.blockText }}</slot>
  </div>
  <ProcedureStep v-for="task of block.tasks" :key="task.taskIndex" :task></ProcedureStep>
</template>
<script setup lang="ts" generic="E extends Entity">
import { computed } from 'vue'

import type { Entity } from '@/types/entities'
import type { Block } from '@/types/procedure'

import ProcedureStep from '../atoms/ProcedureStep.vue'

const props = defineProps<{ block: Block<Entity> }>()

const state = computed(() => {
  if (props.block.tasks.every((task: any) => task.state === 'done')) return 'done'
  if (props.block.tasks.some((task: any) => task.state === 'doing')) return 'doing'
  return 'todo'
})
</script>
<style lang="scss">
.procedure-block {
  scroll-snap-align: start;
  transition: var(--duration);
  border-radius: 8px;
  background: var(--color-grey-300);
  color: #fff;
  padding: 8px;
  width: fit-content;
  margin: 8px 0;
  border: 2px solid var(--color-grey-300);

  &[state='done'] {
    border-color: var(--color-primary);
  }

  &[state='doing'] {
    background: var(--color-primary);
    border-color: var(--color-primary);
  }
}
</style>
