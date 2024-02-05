<template>
  <SVG src="logo" fill="var(--color-primary)" :width="56" class="self-center"></SVG>
  <SpeechBubble>
    <i18n-t scope="global" keypath="event.text">
      <template #event>
        <strong style="color: var(--color-error)">
          {{ card.data?.metadata.id_app }}
        </strong>
      </template>
    </i18n-t>
  </SpeechBubble>
  <div class="flex flex-center-y">
    <Button color="secondary" type="button">{{ $t('event.button.secondary') }}</Button>
    <Info fill="var(--color-grey-600)" stroke="var(--color-background)" :width="20" class="ml-1" />
  </div>
  <div class="flex flex-center-y">
    <Button type="button" @click="eventBus.emit('assistant:tab', 2)">
      {{ $t('event.button.primary') }}
    </Button>
    <Info fill="var(--color-grey-600)" stroke="var(--color-background)" :width="20" class="ml-1" />
  </div>
</template>
<script setup lang="ts">
import { Info } from 'lucide-vue-next'

import Button from '@/components/atoms/Button.vue'
import SpeechBubble from '@/components/atoms/SpeechBubble.vue'
import SVG from '@/components/atoms/SVG.vue'
import eventBus from '@/plugins/eventBus'
import type { Card } from '@/types/cards'

defineProps<{ card: Card<'ORANGE'> }>()
</script>
