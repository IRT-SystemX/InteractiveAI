<template>
  <section class="cab-panel">
    <h1>{{ $t('cab.notifications') }}</h1>
    <div v-if="cardsStore.cards.length" class="card-container">
      <TransitionGroup name="fade">
        <Notification
          v-for="card of cardsStore.cards"
          :key="card.id"
          :severity="card.severity"
          @click="eventBus.emit('assistant:selected', card)">
          <template #title>{{ card.titleTranslated }}</template>
          <template #severity>
            {{ $t(`card.event_type.${card.data!.metadata.event_type}`) }}
            <SVG
              src="icons/warning_hex"
              :fill="`var(--color-${severityToColor(card.severity)})`"
              :width="16"
              class="ml-1"></SVG>
          </template>
          {{ card.summaryTranslated }}
          <template #actions>
            <Button size="small" color="secondary">
              <Star :height="12" fill="currentColor" />
            </Button>
            <Button size="small" color="secondary">
              <MoveRight :height="12" />
              <User :height="12" />
            </Button>
            <Button size="small" color="secondary" @click.stop="deleteCard(card.id)">
              <Trash2 :height="12" />
            </Button>
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
import { MoveRight, Star, Trash2, User } from 'lucide-vue-next'

import { deleteCard } from '@/api/cards'
import Button from '@/components/atoms/Button.vue'
import SVG from '@/components/atoms/SVG.vue'
import Notification from '@/components/molecules/Notification.vue'
import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import { severityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()
</script>
<style lang="scss"></style>
