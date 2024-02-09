<template>
  <Notifications
    entity="RTE"
    :sections="[
      {
        name: 'main',
        weight: 2,
        filter: (card) => filter.includes(card.severity)
      },
      {
        name: 'sub',
        weight: 1,
        filter: (card) => !filter.includes(card.severity)
      }
    ]">
    <template #severity>Sûreté</template>
    <template #icon="{ card }">
      <Zap
        v-if="card.severity === 'ALARM'"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        :height="16" />
      <SVG
        v-else
        src="icons/toolbox"
        :fill="`var(--color-${severityToColor(card.severity)})`"
        :width="16"
        class="ml-1"></SVG>
    </template>
    <template #actions>
      <Button size="small" color="secondary">
        <ChevronUp :height="16" />
      </Button>
      <Button size="small" color="secondary">
        <ChevronDown :height="16" />
      </Button>
      <Button size="small" color="secondary">
        <MoveRight :height="12" />
        <User :height="12" />
      </Button>
    </template>
  </Notifications>
</template>
<script setup lang="ts">
import { ChevronDown, ChevronUp, MoveRight, User, Zap } from 'lucide-vue-next'

import Button from '@/components/atoms/Button.vue'
import SVG from '@/components/atoms/SVG.vue'
import Notifications from '@/components/organisms/CAB/Notifications.vue'
import { severityToColor } from '@/utils/utils'

const filter = ['ALARM', 'ACTION', 'COMPLIANT', 'ND']
</script>
