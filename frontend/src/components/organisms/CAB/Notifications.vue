<template>
  <section class="cab-panel">
    <Modal
      v-for="modal of modals"
      :key="modal.message"
      type="choice"
      @close="(...$event) => closeModal(...$event, modal)">
      {{ modal.message }}
    </Modal>
    <section
      v-for="section of sections"
      :key="section.name"
      class="cab-notifications flex flex-col"
      :style="{
        height: `${(section.weight / sections.reduce((a, b) => a + b.weight, 0)) * 100}%`
      }">
      <h1>{{ $t(`cab.notifications.${section.name}`) }}</h1>
      <div v-if="cards.filter(section.filter).length" class="card-container">
        <TransitionGroup name="fade">
          <Notification
            v-for="card of cards.filter(section.filter)"
            :key="card.id"
            :severity="card.severity"
            @click="selected(card)">
            <template #title>{{ card.titleTranslated }}</template>
            <template #severity>
              <slot name="severity" :card="card">
                {{ format(new Date(card.startDate), 'p') }}
              </slot>
              <slot name="icon" :card="card">
                <SVG
                  src="icons/warning_hex"
                  :fill="`var(--color-${severityToColor(card.severity)})`"
                  :width="16"
                  class="ml-1"></SVG>
              </slot>
            </template>
            {{ card.summaryTranslated }}
            <template #actions>
              <slot name="actions" :card="card">
                <Button size="small" color="secondary">
                  <Trash2 :height="12" @click.stop="confirmDeletion(card)" />
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
  </section>
</template>
<script setup lang="ts" generic="T extends Entity">
import { Trash2 } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { acknowledge } from '@/api/cards'
import Button from '@/components/atoms/Button.vue'
import Modal from '@/components/atoms/Modal.vue'
import SVG from '@/components/atoms/SVG.vue'
import Notification from '@/components/molecules/Notification.vue'
import { format } from '@/plugins/date'
import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { severityToColor } from '@/utils/utils'

const { t } = useI18n()
const cardsStore = useCardsStore()

const props = withDefaults(
  defineProps<{
    sections?: { name: string; weight: number; filter: (card: Card) => boolean }[]
    entity: T
  }>(),
  {
    sections: () => [{ name: 'main', weight: 1, filter: () => true }]
  }
)

const cards = computed(() => cardsStore.cards(props.entity))

const modals = ref<{ callback: (res: 'ok' | 'ko') => void; message: string }[]>([])

function selected(card: Card<T>) {
  // @ts-ignore
  eventBus.emit(`assistant:selected:${props.entity}`, card)
}

function closeModal(_: any, res: 'ok' | 'ko', modal: (typeof modals.value)[0]) {
  modals.value.splice(modals.value.indexOf(modal), 1)
  if (modal.callback) modal.callback(res)
}

function confirmDeletion(card: Card) {
  if (card.severity !== 'ND')
    modals.value.push({
      message: t('cab.notifications.delete', { event: card.titleTranslated }),
      callback: (res) => {
        if (res === 'ok') {
          acknowledge(card)
        }
      }
    })
  else acknowledge(card)
}
</script>
<style lang="scss">
.cab-notifications {
  .card-container {
    overflow: auto;
    scrollbar-gutter: stable;
    height: 100%;
    display: flex;
    gap: var(--spacing-1);
    flex-direction: column;
    scroll-snap-type: y mandatory;
  }

  .card-container-empty {
    display: flex;
    flex: 1;
    align-items: center;
    justify-content: center;
    color: var(--color-grey-300);
    font-weight: 400;
    text-align: center;
  }
}
</style>
