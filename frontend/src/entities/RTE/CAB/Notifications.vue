<template>
  <Notifications
    entity="RTE"
    :sections="[
      {
        name: 'main',
        weight: 2,
        filter: (card) => filter.includes(card.data.criticality)
      },
      {
        name: 'sub',
        weight: 1,
        filter: (card) => !filter.includes(card.data.criticality)
      }
    ]">
    <template #severity>Sûreté</template>
    <template #icon="{ card }">
      <Zap
        v-if="card.severity === 'ALARM'"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :height="16" />
      <SVG
        v-else
        src="icons/toolbox"
        :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
        :width="16"
        class="ml-1"></SVG>
    </template>
    <template #actions="{ card, deletion, hasBeenAcknowledged }">
      <Tooltip>
        <template #tooltip>{{ $t('card.actions.upvote.tooltip') }}</template>
        <Button size="small" color="secondary" @click.stop="vote(card, true)">
          <ChevronUp :height="16" />
        </Button>
      </Tooltip>
      <Tooltip>
        <template #tooltip>{{ $t('card.actions.downvote.tooltip') }}</template>
        <Button size="small" color="secondary" @click.stop="vote(card, false)">
          <ChevronDown :height="16" />
        </Button>
      </Tooltip>
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
import { ChevronDown, ChevronUp, Inbox, Zap } from 'lucide-vue-next'

import { removeEvent } from '@/api/cards'
import Button from '@/components/atoms/Button.vue'
import SVG from '@/components/atoms/SVG.vue'
import Tooltip from '@/components/atoms/Tooltip.vue'
import Notifications from '@/components/organisms/CAB/Notifications.vue'
import type { Card, Criticality } from '@/types/cards'
import { criticalityToColor } from '@/utils/utils'

const filter: Criticality[] = ['HIGH', 'MEDIUM', 'LOW', 'ND']

function vote(card: Card, up: boolean) {
  if (!up) removeEvent(card.processInstanceId)
}
</script>
