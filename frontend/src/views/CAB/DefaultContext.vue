<template>
  <Context :tabs="[$t('cab.tab.context')]">
    {{ servicesStore.context('PowerGrid') }}
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onUnmounted, ref } from 'vue'

import Context from '@/components/organisms/CAB/Context.vue'
import { useServicesStore } from '@/stores/services'

const servicesStore = useServicesStore()

const contextPID = ref(0)

onBeforeMount(async () => {
  contextPID.value = await servicesStore.getContext()
})

onUnmounted(() => {
  clearInterval(contextPID.value)
})
</script>
