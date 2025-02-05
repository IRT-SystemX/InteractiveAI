<template>
  <div class="cab-avatar flex flex-center" :style="{ height: size + 'px', width: size + 'px' }">
    <LoadingVue v-if="loading" color="var(--color-primary)"></LoadingVue>
    <canvas
      ref="canvasHTML"
      :class="{ visible: !loading }"
      :height="size"
      :width="size"
      alt="InteractiveAI robot avatar"
      title="Model by sketchfab.com/MoraAzul"></canvas>
  </div>
</template>
<script setup lang="ts">
import { WebGLRenderer } from 'three'
import { onBeforeUnmount, onMounted, ref, watchEffect } from 'vue'

import { changeTexture, loading, setup } from '@/plugins/avatar'

import LoadingVue from './Loading.vue'

const props = withDefaults(
  defineProps<{
    size: number
    status?: 'default' | 'error' | 'warning' | 'success' | 'primary' | 'secondary'
  }>(),
  {
    size: 100,
    status: 'default'
  }
)

const canvasHTML = ref<HTMLCanvasElement>()
let renderer: WebGLRenderer

watchEffect(() => changeTexture(props.status))
onMounted(() => {
  renderer = setup(canvasHTML.value!)
})

onBeforeUnmount(() => {
  renderer.dispose()
})
</script>
<style scoped>
.cab-avatar {
  position: relative;
  img {
    position: absolute;
  }
  canvas {
    position: absolute;
    opacity: 0;
    transition: 1s;
    &.visible {
      opacity: 1;
    }
  }
}
</style>
