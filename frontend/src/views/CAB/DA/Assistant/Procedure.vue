<template>
  <main>
    <ProcedureBlock v-for="block of procedure" :key="block.blockIndex" :block="block" />
  </main>
</template>
<script setup lang="ts">
import ProcedureBlock from '@/components/molecules/ProcedureBlock.vue'

defineProps<{ procedure: any[] }>()
</script>
