<template>
  <Context :tabs="[$t('cab.tab.context')]">
    {{ servicesStore.context('PowerGrid') }}
  </Context>
</template>
<script setup lang="ts">
import { onBeforeMount, onUnmounted } from 'vue'

import Context from '@/components/organisms/CAB/Context.vue'
import { useServicesStore } from '@/stores/services'

const servicesStore = useServicesStore()


onBeforeMount(async () => {
  await servicesStore.getContext()
})

onUnmounted(() => {
  servicesStore.stopContext()
})
</script>
