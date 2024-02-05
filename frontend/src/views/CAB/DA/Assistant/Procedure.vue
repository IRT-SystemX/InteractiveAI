<template>
  <div>
    <ProcedureBlock v-for="block of procedure" :key="block.blockIndex" :block="block" />
  </div>
</template>
<script setup lang="ts">
import { computed, onBeforeMount, ref } from 'vue'

import { getProcedure } from '@/api/services/DA'
import ProcedureBlock from '@/components/molecules/ProcedureBlock.vue'
import eventBus from '@/plugins/eventBus'

const procedure = ref<any[]>([])
const tasks = computed(() => procedure.value?.flatMap((block) => block.tasks))

onBeforeMount(async () => {
  const { data } = await getProcedure()
  procedure.value = data.procedure
  procedure.value[0].tasks[0].state = 'doing'
})

eventBus.on('assistant:procedure:checked', (task) => {
  task.state = 'done'
  tasks.value[tasks.value?.findIndex((t) => t.taskIndex === task.taskIndex) + 1].state = 'doing'
})
</script>
