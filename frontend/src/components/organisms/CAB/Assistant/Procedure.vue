<template>
  <label>
    <b>
      <i18n-t keypath="cab.assistant.procedure.collaborate">
        <template #cab>
          <b class="cab-logo-typo">{{ $t('cab') }}</b>
        </template>
      </i18n-t>
    </b>
    <Switch v-model="collaboration" type="checkbox" class="ml-1" />
  </label>
  <div v-if="collaboration" class="cab-procredure-header">
    <User :size="24" style="justify-self: left" class="ml-2" />
    <SVG
      src="/img/logo.svg"
      :width="24"
      style="justify-self: right; grid-column: 3"
      class="mr-2"></SVG>
  </div>
  <div class="flex flex-1 flex-col scrollable">
    <ProcedureBlock v-for="block of procedure" :key="block.blockIndex" :block :collaboration />
  </div>
</template>
<script setup lang="ts" generic="E extends Entity">
import { User } from 'lucide-vue-next'
import { computed, provide, ref } from 'vue'

import SVG from '@/components/atoms/SVG.vue'
import Switch from '@/components/atoms/Switch.vue'
import ProcedureBlock from '@/components/molecules/ProcedureBlock.vue'
import type { Entity } from '@/types/entities'
import type { Procedure, Step } from '@/types/procedure'

const props = defineProps<{ procedure: Procedure<E>['procedure'] }>()

const collaboration = ref(false)

const tasks = computed(() => props.procedure.flatMap((block) => block.tasks))

provide('checkTask', (task: Step) => {
  task.state = 'done'
  tasks.value[tasks.value?.findIndex((t) => t.taskIndex === task.taskIndex) + 1].state = 'doing'
})
</script>
<style lang="scss">
.cab-procredure-header {
  display: grid;
  height: calc(var(--unit) * 5);
  grid-template-columns: calc(50% - var(--unit)) calc(var(--unit) * 2) calc(50% - var(--unit));
  justify-items: center;
  margin-bottom: calc(var(--unit) * -7);
  align-content: center;
  z-index: 101;
}
</style>
