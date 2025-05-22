<template>
  <Notifications
    entity="PowerGrid"
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
    ]"
    :selection="
      (card) => {
        card.read = true
        appStore._card = card.severity === 'INFORMATION' ? undefined : card
      }
    ">
    <template #severity>Sûreté</template>
    <template #icon="{ card }">
      <Zap
        v-if="card.severity === 'ALARM'"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :color="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :height="16" />
      <SVG
        v-else
        src="/img/icons/toolbox.svg"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :width="16"
        class="ml-1"></SVG>
    </template>
    <template #actions="{ card, deletion, hasBeenAcknowledged }">
      <Tooltip v-if="!hasBeenAcknowledged">
        <template #tooltip>{{ $t('card.actions.delete.tooltip') }}</template>
        <Button size="small" color="secondary" @click.stop="deletion(card)">
          <Inbox :height="12" />
        </Button>
      </Tooltip>
    </template>
  </Notifications>
</template>
<script setup lang="ts">
import { Inbox, Zap } from 'lucide-vue-next'

import Button from '@/components/atoms/Button.vue'
import SVG from '@/components/atoms/SVG.vue'
import Tooltip from '@/components/atoms/Tooltip.vue'
import Notifications from '@/components/organisms/CAB/Notifications.vue'
import { useAppStore } from '@/stores/app'
import type { Criticality } from '@/types/cards'
import { criticalityToColor } from '@/utils/utils'

const FILTER: Criticality[] = ['HIGH', 'MEDIUM', 'LOW', 'ND']

const appStore = useAppStore()
</script>
