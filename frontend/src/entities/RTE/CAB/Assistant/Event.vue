<template>
  <SVG src="logo" fill="var(--color-primary)" :width="56" class="self-center"></SVG>
  <SpeechBubble>
    <i18n-t scope="global" keypath="event.text">
      <template #event>
        <strong :style="{ color: `var(--color-${severityToColor(card.severity)})` }">
          {{ card.titleTranslated }}
        </strong>
      </template>
    </i18n-t>
  </SpeechBubble>
  <div class="flex flex-center-y">
    <Button type="button" @click="askRecommendations">{{ $t('event.button.primary') }}</Button>
    <Info fill="var(--color-grey-600)" stroke="var(--color-background)" :width="20" class="ml-1" />
  </div>
  <div class="flex flex-center-y">
    <Button type="button" color="secondary">{{ $t('event.button.secondary') }}</Button>
    <Info fill="var(--color-grey-600)" stroke="var(--color-background)" :width="20" class="ml-1" />
  </div>
</template>
<script setup lang="ts">
import { Info } from 'lucide-vue-next'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import Button from '@/components/atoms/Button.vue'
import SpeechBubble from '@/components/atoms/SpeechBubble.vue'
import SVG from '@/components/atoms/SVG.vue'
import eventBus from '@/plugins/eventBus'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { Trace } from '@/types/services'
import { severityToColor } from '@/utils/utils'

defineProps<{ card: Card<'RTE'> }>()

const route = useRoute()

function askRecommendations() {
  sendTrace({
    data: {} as Trace['data'],
    use_case: route.params.entity as Entity,
    step: 'ASKFORHELP'
  })
  eventBus.emit('assistant:tab', 2)
}
</script>
