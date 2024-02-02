<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.notifications') }}</h1>
    <div v-if="cardsStore.cards('ORANGE').length" class="card-container">
      <TransitionGroup name="fade">
        <Notification
          v-for="card of cardsStore.cards('ORANGE')"
          :key="card.id"
          :severity="card.severity"
          @click="eventBus.emit('assistant:selected:ORANGE', card)">
          <template #title>{{ card.titleTranslated }}</template>
          <template #severity>
            {{ format(card.startDate, 'p') }}
            <CheckCircle2
              v-if="card.severity === 'INFORMATION'"
              :fill="`var(--color-${severityToColor(card.severity)})`"
              stroke="var(--color-background)"
              :width="20"
              class="ml-1" />
            <SVG
              v-else
              src="icons/warning_hex"
              :fill="`var(--color-${severityToColor(card.severity)})`"
              :width="16"
              class="ml-1"></SVG>
          </template>
          {{ card.summaryTranslated }}
          <template #actions>
            <Button size="small" color="secondary">
              <Trash2 :height="12" @click.stop="acknowledgeCard(card)" />
            </Button>
            <Button size="small" color="secondary"><Settings :height="12" /></Button>
          </template>
        </Notification>
      </TransitionGroup>
    </div>
    <div v-else class="card-container-empty">
      {{ $t('cab.notifications.empty') }}
    </div>
  </section>
</template>
<script setup lang="ts">
import { Settings, Trash2 } from 'lucide-vue-next'
import { CheckCircle2 } from 'lucide-vue-next'

import { acknowledgeCard } from '@/api/cards'
import Button from '@/components/atoms/Button.vue'
import SVG from '@/components/atoms/SVG.vue'
import Notification from '@/components/molecules/Notification.vue'
import { format } from '@/plugins/date'
import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import { severityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()
</script>
