<template>
  <Notifications entity="Railway">
    <template #severity="{ card }">
      {{
        $t(`card.event_type.${card.data.metadata.event_type}`) !==
        `card.event_type.${card.data.metadata.event_type}`
          ? $t(`card.event_type.${card.data.metadata.event_type}`)
          : card.data.metadata.event_type
      }}
    </template>
    <template #actions="{ card, deletion, hasBeenAcknowledged }">
      <Tooltip>
        <template #tooltip>
          {{ $t('card.actions.move_user.tooltip') }}
        </template>
        <Button size="small" color="secondary">
          <MoveRight :height="12" />
          <User :height="12" />
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
import { Inbox, MoveRight, User } from 'lucide-vue-next'

import Button from '@/components/atoms/Button.vue'
import Tooltip from '@/components/atoms/Tooltip.vue'
import Notifications from '@/components/organisms/CAB/Notifications.vue'
</script>
