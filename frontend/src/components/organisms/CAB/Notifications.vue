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
      <header class="flex flex-between">
        <h1>
          {{ $t(`cab.notifications.${section.name}`) }}
          {{ hasBeenAcknowledged ? $t('cab.notifications.archived') : '' }}
        </h1>
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
      </header>
      <div v-if="Object.keys(filtered(section.filter)).length" class="card-container">
        <template
          v-for="key of Object.keys(filtered(section.filter)).sort((a, b) => {
            return (
              CriticalityArray.indexOf(
                filtered(section.filter)[b].reduce(
                  (prev: Criticality, curr) =>
                    CriticalityArray.indexOf(curr.data.criticality) > CriticalityArray.indexOf(prev)
                      ? curr.data.criticality
                      : prev,
                  'ND'
                )
              ) -
              CriticalityArray.indexOf(
                filtered(section.filter)[a].reduce(
                  (prev: Criticality, curr) =>
                    CriticalityArray.indexOf(curr.data.criticality) > CriticalityArray.indexOf(prev)
                      ? curr.data.criticality
                      : prev,
                  'ND'
                )
              )
            )
          })"
          :key>
          <Notification
            v-if="key !== '_DEFAULT'"
            :criticality="
              filtered(section.filter)[key].reduce(
                (prev: Criticality, curr) =>
                  CriticalityArray.indexOf(curr.data.criticality) > CriticalityArray.indexOf(prev)
                    ? curr.data.criticality
                    : prev,
                'ND'
              )
            ">
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
import { ChevronDown, Inbox } from 'lucide-vue-next'
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
import { type Card, type Criticality, CriticalityArray } from '@/types/cards'
import type { Entity } from '@/types/entities'
import { criticalityToColor } from '@/utils/utils'

const { t } = useI18n()
const cardsStore = useCardsStore()

const props = withDefaults(
  defineProps<{
    sections?: { name: string; weight: number; filter: (card: Card) => boolean }[]
    groupFn?: (card: Card<T>) => string
    entity: T
  }>(),
  {
    sections: () => [{ name: 'main', weight: 1, filter: () => true }],
    groupFn: () => '_DEFAULT'
  }
)

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
const modals = ref<{ callback: (res: 'ok' | 'ko') => void; message: string }[]>([])

const active = ref<Card['id'][]>([])

eventBus.on('notifications:close', (card) => {
  active.value.push(card.id)
  modals.value.push({
    message: t('cab.notifications.ended'),
    callback: (res) => {
      active.value = []
      if (res === 'ok') {
        cardsStore.acknowledge(card)
      }
    }
  })
})

function closeModal(_: any, res: 'ok' | 'ko', modal: (typeof modals.value)[0]) {
  modal.callback(res)
  modals.value.splice(modals.value.indexOf(modal), 1)
}

function confirmDeletion(card: Card) {
  if (card.data.criticality !== 'ND') {
    active.value.push(card.id)
    modals.value.push({
      message: t('cab.notifications.delete', { event: card.titleTranslated }),
      callback: (res) => {
        active.value = []
        if (res === 'ok') {
          cardsStore.acknowledge(card)
        }
      }
    })
  } else cardsStore.acknowledge(card)
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
