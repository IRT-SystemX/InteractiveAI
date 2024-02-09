<template>
  <section class="cab-panel">
    <Modal
      v-for="modal of modals"
      :key="modal"
      type="choice"
      @close="modals.splice(modals.indexOf(modal), 1)">
      {{ modal }}
    </Modal>
    <div class="cab-notifications-main flex flex-col">
      <section
        v-for="section of sections"
        :key="section.name"
        :style="{ height: `${(section.size / sections.reduce((a, b) => a + b.size, 0)) * 100}%` }">
        <h1>{{ $t(`cab.notifications.${section.name}`) }}</h1>
        <div v-if="cardsStore.cards('DA').filter(section.filter).length" class="card-container">
          <TransitionGroup name="fade">
            <Notification
              v-for="card of cardsStore.cards('DA').filter(section.filter)"
              :key="card.id"
              :severity="card.severity"
              @click="eventBus.emit('assistant:selected:DA', card)">
              <template #title>{{ card.titleTranslated }}</template>
              <template #severity>
                <slot name="severity">
                  {{ format(new Date(card.startDate), 'p') }}
                  <slot name="icon">
                    <SVG
                      src="icons/warning_hex"
                      :fill="`var(--color-${severityToColor(card.severity)})`"
                      :width="16"
                      class="ml-1"></SVG>
                  </slot>
                </slot>
              </template>
              {{ card.summaryTranslated }}
              <template #actions>
                <slot name="actions">
                  <Button size="small" color="secondary">
                    <Trash2 :height="12" @click.stop="acknowledge(card)" />
                  </Button>
                </slot>
              </template>
            </Notification>
          </TransitionGroup>
        </div>
        <div v-else class="card-container-empty">
          {{ $t('cab.notifications.empty') }}
        </div>
      </section>
    </div>
  </section>
</template>
<script setup lang="ts">
import { Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'

import { acknowledge } from '@/api/cards'
import Button from '@/components/atoms/Button.vue'
import Modal from '@/components/atoms/Modal.vue'
import SVG from '@/components/atoms/SVG.vue'
import Notification from '@/components/molecules/Notification.vue'
import { format } from '@/plugins/date'
import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import type { Card } from '@/types/cards'
import { severityToColor } from '@/utils/utils'

const cardsStore = useCardsStore()

withDefaults(
  defineProps<{ sections?: { name: string; size: number; filter: (card: Card) => boolean }[] }>(),
  {
    sections: () => [{ name: 'notification', size: 1, filter: () => true }]
  }
)

const modals = ref<any[]>([])
</script>
