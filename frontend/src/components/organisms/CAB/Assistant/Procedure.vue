<template>
  <div>
    <label>
      {{ $t('cab.assistant.procedure.collaborate') }}
      <input v-model="collaboration" type="checkbox" />
    </label>
    <ProcedureBlock v-for="block of procedure" :key="block.blockIndex" :block />
  </div>
</template>
<script setup lang="ts" generic="E extends Entity">
import { computed, ref } from 'vue'

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
