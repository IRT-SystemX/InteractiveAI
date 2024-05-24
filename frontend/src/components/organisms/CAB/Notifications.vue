<template>
  <section class="cab-panel">
    <Modal
      v-for="modal of modals"
      :key="modal.message"
      type="choice"
      @close="closeModal($event, modal)">
      {{ modal.message }}
    </Modal>
    <section
      v-for="(section, index) of sections"
      :key="section.name"
      class="cab-notifications flex flex-col"
      :style="{
        height: `${(section.weight / sections.reduce((a, b) => a + b.weight, 0)) * 100}%`
      }">
      <header class="flex flex-between">
        <h1>
          {{ $t(`cab.notifications.${section.name}`) }}
          {{ hasBeenAcknowledged ? $t('cab.notifications.archived') : '' }}
        </h1>
        <div v-if="index === 0" class="flex">
          <Tooltip>
            <template #tooltip>
              {{ $t(`cab.notifications.button.delete_all`) }}
            </template>
            <button>
              <Eraser @click="deleteAll" />
            </button>
          </Tooltip>
          <Tooltip>
            <template #tooltip>
              {{ $t(`cab.notifications.${section.name}`) }}
              {{ $t('cab.notifications.archived') }}
            </template>
            <button>
              <Inbox
                :stroke="hasBeenAcknowledged ? 'var(--color-primary)' : 'currentColor'"
                @click="hasBeenAcknowledged = !hasBeenAcknowledged" />
            </button>
          </Tooltip>
        </div>
      </header>
      <div v-if="Object.keys(filtered(section.filter)).length" class="card-container">
        <template
          v-for="key of Object.keys(filtered(section.filter)).sort((a, b) => {
            return (
              CriticalityArray.indexOf(maxCriticality('ND', filtered(section.filter)[b])) -
              CriticalityArray.indexOf(maxCriticality('ND', filtered(section.filter)[a]))
            )
          })"
          :key>
          <Notification
            v-if="key !== '_DEFAULT'"
            :criticality="maxCriticality('ND', filtered(section.filter)[key])">
            <div class="flex flex-center-y flex-gap">
              <ChevronDown />
              <header
                class="flex flex-1"
                :style="{
                  color: filtered(section.filter)[key].every((c) => c.read)
                    ? 'var(--color-grey-600)'
                    : undefined
                }">
                <b class="flex-1">Application {{ +/\d+/.exec(key)![0] }}</b>
                <aside>
                  {{ $t('cab.notifications.group', filtered(section.filter)[key].length) }}
                </aside>
              </header>
            </div>
          </Notification>
          <NotificationTreeNode
            v-for="c of filtered(section.filter)[key]"
            :key="c.id"
            :card="c"
            :is-child="key !== '_DEFAULT'">
            <template #title="{ card }">
              <slot name="title" :card>{{ card.titleTranslated }}</slot>
            </template>
            <template #severity="{ card }">
              <slot name="severity" :card>
                {{ format(new Date(card.startDate), 'p') }}
              </slot>
              <slot name="icon" :card>
                <SVG
                  src="/img/icons/warning_hex.svg"
                  :fill="`var(--color-${criticalityToColor(card.data.criticality)})`"
                  :width="16"
                  class="ml-1"></SVG>
              </slot>
            </template>
            <template #default="{ card }">
              <slot>
                {{ card.summaryTranslated }}
              </slot>
            </template>
            <template #actions="{ card }">
              <slot
                name="actions"
                :card
                :deletion="confirmDeletion"
                :has-been-acknowledged="hasBeenAcknowledged">
                <Tooltip v-if="!hasBeenAcknowledged">
                  <template #tooltip>{{ $t('card.actions.delete.tooltip') }}</template>
                  <Button
                    size="small"
                    color="secondary"
                    :aria-label="$t('cab.notifications.archived')">
                    <Inbox :height="12" @click.stop="confirmDeletion(card)" />
                  </Button>
                </Tooltip>
              </slot>
            </template>
          </NotificationTreeNode>
        </template>
      </div>
      <div v-else class="card-container-empty">
        {{ $t('cab.notifications.empty') }}
      </div>
    </section>
  </section>
</template>
<script setup lang="ts" generic="T extends Entity">
import { ChevronDown, Eraser, Inbox } from 'lucide-vue-next'
import groupBy from 'object.groupby'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import Button from '@/components/atoms/Button.vue'
import Modal from '@/components/atoms/Modal.vue'
import SVG from '@/components/atoms/SVG.vue'
import Tooltip from '@/components/atoms/Tooltip.vue'
import Notification from '@/components/molecules/Notification.vue'
import NotificationTreeNode from '@/components/organisms/NotificationTreeNode.vue'
import { format } from '@/plugins/date'
import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import { type Card, CriticalityArray } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { criticalityToColor, maxCriticality } from '@/utils/utils'

const props = withDefaults(
  defineProps<{
    autoclose?: boolean
    sections?: { name: string; weight: number; filter: (card: Card) => boolean }[]
    groupFn?: (card: Card<T>) => string
    entity: T
  }>(),
  {
    autoclose: true,
    sections: () => [{ name: 'main', weight: 1, filter: () => true }],
    groupFn: () => '_DEFAULT'
  }
)

const { t } = useI18n()
const cardsStore = useCardsStore()

const cards = computed(() =>
  [...cardsStore.cards(props.entity, hasBeenAcknowledged.value)].sort(
    (a, b) =>
      CriticalityArray.indexOf(b.data.criticality) - CriticalityArray.indexOf(a.data.criticality)
  )
)

function filtered(fn: (typeof props.sections)[number]['filter']) {
  return groupBy(cardsStore.parseTree(cards.value.filter(fn)), props.groupFn)
}

const hasBeenAcknowledged = ref(false)
const modals = ref<{ callback: (success: boolean) => void; message: string; id: string }[]>([])

eventBus.on('notifications:ended', () => {
  if (modals.value.find((m) => m.id === 'ended') || !props.autoclose) return
  modals.value.push({
    message: t('cab.notifications.ended'),
    id: 'ended',
    callback: (success) => {
      if (success) {
        for (const card of cardsStore
          .cards(props.entity)
          .filter((c) => c.data.criticality === 'ND'))
          cardsStore.acknowledge(card)
      }
    }
  })
})

function closeModal(success: boolean, modal: (typeof modals.value)[0]) {
  modal.callback(success)
  modals.value.splice(modals.value.indexOf(modal), 1)
}

function confirmDeletion(card: Card) {
  if (card.data.criticality !== 'ND') {
    modals.value.push({
      message: t('cab.notifications.delete', { event: card.titleTranslated }),
      id: 'confirm',
      callback: (success) => {
        if (success) {
          cardsStore.acknowledge(card)
        }
      }
    })
  } else cardsStore.acknowledge(card)
}

function deleteAll() {
  modals.value.push({
    message: t('cab.notifications.delete_all'),
    id: 'confirm',
    callback: (success) => {
      if (success) {
        for (const card of cardsStore.cards(props.entity)) cardsStore.acknowledge(card)
      }
    }
  })
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

  .cab-notification.selected {
    z-index: 2500;
  }
}
</style>
