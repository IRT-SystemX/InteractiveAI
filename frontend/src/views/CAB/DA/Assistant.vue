<template>
  <section class="cab-panel">
    <Default>
      <Procedure v-if="tab === 1" />
      <Recommendations v-if="tab === 2" />
    </Default>
  </section>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import eventBus from '@/plugins/eventBus'

import Default from '../Common/Assistant/Default.vue'
import Procedure from './Assistant/Procedure.vue'
import Recommendations from './Assistant/Recommendations.vue'

const tab = ref(0)

eventBus.on('assistant:selected', async (selectedCard) => {
  tab.value = 1
  const firstClickPromise = new Promise((resolve) => {
    document.getElementsByClassName("cab-tab")[1].addEventListener("click", resolve, { once: true });
    document.getElementsByClassName("cab-tab")[1].click();
  });
  await firstClickPromise;
  document.getElementById("ecs").click();
})
eventBus.on('assistant:tab', (index) => {
  tab.value = index
})
</script>
<style lang="scss" scoped>
.cab-assistant main {
  overflow: auto;
  scroll-snap-type: y mandatory;
}
</style>
@/stores/components/map
