<!--https://stackabuse.com/lazy-loading-routes-with-vue-router-->
<template>
  <div
    :class="{
      'loading-container': true,
      loading: isLoading,
      visible: isVisible
    }">
    <div class="loader" :style="{ width: progress + '%' }">
      <div class="light animated" />
    </div>
    <div class="glow" />
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import eventBus from '@/plugins/eventBus'
import { randomInt } from '@/utils/utils'

// Assume that loading will complete under this amount of time.
const defaultDuration = 4000
// How frequently to update
const defaultInterval = 200
// 0 - 1. Add some variation to how much the bar will grow at each interval
const variation = 0.5
// 0 - 100. Where the progress bar should start from.
const startingPoint = 0
// Limiting how far the progress bar will get to before loading is complete
const endingPoint = 90

const isLoading = ref(true) // Once loading is done, start fading away
const isVisible = ref(false) // Once animate finish, set display: none
const progress = ref(startingPoint)
const timeoutId = ref<number>()

function loop() {
  if (timeoutId.value) {
    clearTimeout(timeoutId.value)
  }
  if (progress.value >= endingPoint) {
    return
  }
  const size = (endingPoint - startingPoint) / (defaultDuration / defaultInterval)
  const p = Math.round(progress.value + randomInt(size * (1 - variation), size * (1 + variation)))
  progress.value = Math.min(p, endingPoint)
  timeoutId.value = window.setTimeout(
    loop,
    randomInt(defaultInterval * (1 - variation), defaultInterval * (1 + variation))
  )
}

function start() {
  isLoading.value = true
  isVisible.value = true
  progress.value = startingPoint
  loop()
}

function stop() {
  isLoading.value = false
  progress.value = 100
  clearTimeout(timeoutId.value)
  setTimeout(() => {
    if (!isLoading.value) {
      isVisible.value = false
    }
  }, 2000)
}

eventBus.on('progress:start', start)
eventBus.on('progress:stop', stop)
</script>
<style scoped>
.loading-container {
  font-size: 0; /* remove space */
  position: fixed;
  top: 0;
  left: 0;
  height: 5px;
  width: 100%;
  opacity: 0;
  display: none;
  z-index: 100;
  transition: opacity 1s;
}

.loading-container.visible {
  display: block;
}
.loading-container.loading {
  opacity: 1;
}

.loader {
  background: var(--color-primary);
  display: inline-block;
  height: 100%;
  width: 50%;
  overflow: hidden;
  border-radius: 0 0 5px 0;
  transition: 0.2s;
}

.loader > .light {
  float: right;
  height: 100%;
  width: 20%;
  background-image: linear-gradient(to right, var(--color-primary), #fff, var(--color-primary));
  animation: loading-animation 2s ease-in infinite;
}

.glow {
  display: inline-block;
  height: 100%;
  width: 30px;
  margin-left: -30px;
  border-radius: 0 0 5px 0;
  box-shadow: 0 0 10px var(--color-primary);
}

@keyframes loading-animation {
  0% {
    margin-right: 100%;
  }
  50% {
    margin-right: 100%;
  }
  100% {
    margin-right: -10%;
  }
}
</style>
