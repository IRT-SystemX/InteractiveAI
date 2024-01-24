<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    :width="width ?? height"
    :height="height ?? width"
    @contextmenu.prevent>
    <use :href="`/img/${src}.svg#root`" :color="fill" :stroke="stroke" />
  </svg>
</template>
<script setup lang="ts">
defineProps<{
  src: string
  fill?: string
  stroke?: string
  width?: number
  height?: number
}>()
</script>
