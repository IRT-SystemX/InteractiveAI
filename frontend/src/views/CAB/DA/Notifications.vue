<template>
  <section class="cab-panel">
    <div class="cab-notifications-main flex flex-col">
      <h1>{{ $t('cab.notifications') }}</h1>
      <div
        v-if="
          cardsStore.cards.filter((card) =>
            ['ALARM', 'ACTION', 'COMPLIANT'].includes(card.severity)
          ).length
        "
        class="card-container">
        <TransitionGroup name="fade">
          <Notification
            v-for="card of cardsStore.cards.filter((card) =>
              ['ALARM', 'ACTION', 'COMPLIANT'].includes(card.severity)
            )"
            :key="card.id"
            :severity="card.severity"
            @click="eventBus.emit('assistant:selectedCard', card)">
            <template #title>{{ card.titleTranslated }}</template>
            <template #severity>
              {{ format(new Date(card.startDate), 'p') }}
              <SVG
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
            </template>
          </Notification>
        </TransitionGroup>
      </div>
      <div v-else class="card-container-empty">
        {{ $t('cab.notifications.empty') }}
      </div>
    </div>
    <div class="cab-notifications-sub flex flex-col">
      <h1>{{ $t('cab.notifications.sub') }}</h1>
      <div
        v-if="cardsStore.cards.filter((card) => ['INFORMATION'].includes(card.severity)).length"
        class="card-container">
        <TransitionGroup name="fade">
          <Notification
            v-for="card of cardsStore.cards.filter((card) =>
              ['INFORMATION'].includes(card.severity)
            )"
            :key="card.id"
            :severity="card.severity"
            @click="eventBus.emit('assistant:selectedCard', card)">
            <template #title>{{ card.titleTranslated }}</template>
            <template #severity>{{ card.severity }}</template>
            {{ card.summaryTranslated }}
            <template #actions>
              <Button size="small" color="secondary">
                <Trash2 :height="12" @click.stop="acknowledgeCard(card)" />
              </Button>
            </template>
          </Notification>
        </TransitionGroup>
      </div>
      <div v-else class="card-container-empty">
        {{ $t('cab.notifications.empty') }}
      </div>
    </div>
  </section>
</template>
<script setup lang="ts">
import { Trash2 } from 'lucide-vue-next'

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
<style lang="scss" scoped></style>
