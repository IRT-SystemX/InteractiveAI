<template>
  <svg
    class="cab-svg"
    xmlns="http://www.w3.org/2000/svg"
    :width="width ?? height"
    :height="height ?? width"
    @contextmenu.prevent>
    <use :href="`${src}#root`" :color="fill" :stroke />
  </svg>
</template>
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  src: string
  fill?: string
  stroke?: string
  width?: number
  height?: number
}>()

const shadow = computed(() => Math.max(props.width ?? 0, props.height ?? 0) / 64)
</script>
<style lang="scss">
.cab-svg {
  filter: drop-shadow(
      calc(var(--unit) * v-bind(shadow) * 0.5) calc(var(--unit) * v-bind(shadow) * 0.5)
        calc(var(--unit) * v-bind(shadow)) color-mix(in srgb, var(--color-background), #000 20%)
    )
    drop-shadow(
      calc(var(--unit) * v-bind(shadow) * -0.5) calc(var(--unit) * v-bind(shadow) * -0.5)
        calc(var(--unit) * v-bind(shadow)) color-mix(in srgb, var(--color-background), #ccc 20%)
    );
}
</style>
