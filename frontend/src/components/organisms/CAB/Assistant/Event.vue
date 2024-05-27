<template>
  <Avatar
    v-if="chatbot"
    :size="200"
    class="self-center"
    :status="criticalityToColor(card.data.criticality)" />
  <SpeechBubble position="bottom" arrow="left">
    <slot name="event">
      <i18n-t scope="global" keypath="event.text">
        <template #event>
          <strong :style="{ color: `var(--color-${criticalityToColor(card.data.criticality)}` }">
            <slot></slot>
          </strong>
        </template>
      </i18n-t>
    </slot>
  </SpeechBubble>
  <div class="flex flex-center-y">
    <Button type="button" @click="primaryAction">
      <slot name="button-primary">
        {{ $t('event.button.primary') }}
      </slot>
    </Button>
    <Tooltip placement="bottom-end" class="ml-1">
      <template #tooltip>
        {{ $t('event.tooltip.primary') }}
      </template>
      <Info fill="var(--color-grey-600)" stroke="var(--color-background)" :width="20" />
    </Tooltip>
  </div>
  <div v-if="secondaryAction" class="flex flex-center-y">
    <Button type="button" color="secondary" @click="secondaryAction">
      <slot name="button-secondary">
        {{ $t('event.button.secondary') }}
      </slot>
    </Button>
    <Tooltip placement="bottom-end" class="ml-1">
      <template #tooltip>
        {{ $t('event.tooltip.secondary') }}
      </template>
      <Info fill="var(--color-grey-600)" stroke="var(--color-background)" :width="20" />
    </Tooltip>
  </div>
</template>
<script setup lang="ts">
import { Info } from 'lucide-vue-next'

import Avatar from '@/components/atoms/Avatar.vue'
import Button from '@/components/atoms/Button.vue'
import SpeechBubble from '@/components/atoms/SpeechBubble.vue'
import Tooltip from '@/components/atoms/Tooltip.vue'
import { useAppStore } from '@/stores/app'
import type { Card } from '@/types/cards'
import { criticalityToColor } from '@/utils/utils'

withDefaults(
  defineProps<{
    chatbot?: boolean
    card: Card
    primaryAction?: (card?: Card) => void
    secondaryAction?: (card?: Card) => void
  }>(),
  {
    primaryAction: () => {
      useAppStore().tab.assistant = 2
    },
    secondaryAction: undefined,
    chatbot: true
  }
)
</script>
