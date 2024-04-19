<template>
  <label>
    {{ $t('cab.assistant.procedure.collaborate') }}
    <Switch v-model="collaboration" type="checkbox" />
  </label>
  <div v-if="collaboration" class="cab-procredure-header">
    <User :size="24" />
    <SVG src="logo" :width="24" :style="{ gridColumn: 3 }"></SVG>
  </div>
  <div class="flex flex-1 flex-col scrollable">
    <ProcedureBlock v-for="block of procedure" :key="block.blockIndex" :block :collaboration />
  </div>
</template>
<script setup lang="ts" generic="E extends Entity">
import { User } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import SVG from '@/components/atoms/SVG.vue'
import Switch from '@/components/atoms/Switch.vue'
import ProcedureBlock from '@/components/molecules/ProcedureBlock.vue'
import eventBus from '@/plugins/eventBus'
import type { Entity } from '@/types/entities'
import type { Procedure } from '@/types/procedure'

const tasks = computed(() => props.procedure.flatMap((block) => block.tasks))

const props = defineProps<{ procedure: Procedure<E>['procedure'] }>()

const collaboration = ref(false)

eventBus.on('assistant:procedure:checked', (task) => {
  task.state = 'done'
  tasks.value[tasks.value?.findIndex((t) => t.taskIndex === task.taskIndex) + 1].state = 'doing'
})
</script>
<style lang="scss">
.cab-procredure-header {
  display: grid;
  grid-template-columns: calc(50% - var(--unit)) calc(var(--unit) * 2) calc(50% - var(--unit));
  justify-items: center;
}
</style>
