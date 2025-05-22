<template>
  <Notifications
    entity="ATM"
    :sections="[
      {
        name: 'main',
        weight: 2,
        filter: (card) => FILTER.includes(card.data.criticality)
      },
      {
        name: 'sub',
        weight: 1,
        filter: (card) => !FILTER.includes(card.data.criticality)
      }
    ]"></Notifications>
</template>
<script setup lang="ts">
import Notifications from '@/components/organisms/CAB/Notifications.vue'
import type { Criticality } from '@/types/cards'

const FILTER: Criticality[] = ['HIGH', 'MEDIUM', 'LOW', 'ND']
</script>
