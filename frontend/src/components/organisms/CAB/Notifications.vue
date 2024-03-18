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
      <div v-if="Object.keys(cards).length" class="card-container">
        <template v-for="(tree, key) of cards" :key="key">
          <Notification
            v-if="key !== '_DEFAULT'"
            :criticality="
              tree.reduce(
                (prev: Criticality, curr) =>
                  CriticalityArray.indexOf(curr.data.criticality) > CriticalityArray.indexOf(prev)
                    ? curr.data.criticality
                    : prev,
                'ND'
              )
            ">
            <div class="flex flex-center-y flex-gap">
              <ChevronDown />
              <header class="flex flex-1">
                <b class="flex-1">Application {{ key }}</b>
                <aside>{{ $t('cab.notifications.group', tree.length) }}</aside>
              </header>
            </div>
          </Notification>
          <NotificationTreeNode
            v-for="c of tree"
            :key="c.id"
            :card="c"
            :is-child="key !== '_DEFAULT'">
            <template #title="{ card }">{{ card.titleTranslated }}</template>
            <template #severity="{ card }">
              <slot name="severity" :card="card">
                {{ format(new Date(card.startDate), 'p') }}
              </slot>
              <slot name="icon" :card="card">
                <SVG
                  src="icons/warning_hex"
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
                :card="card"
                :deletion="confirmDeletion"
                :has-been-acknowledged="hasBeenAcknowledged">
                <Tooltip v-if="!hasBeenAcknowledged">
                  <template #tooltip>{{ $t('card.actions.delete.tooltip') }}</template>
                  <Button size="small" color="secondary">
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

import { acknowledge } from '@/api/cards'
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
  groupBy(cardsStore.tree(cardsStore.cards(props.entity, hasBeenAcknowledged.value)), props.groupFn)
)

const hasBeenAcknowledged = ref(false)
const modals = ref<{ callback?: (res: 'ok' | 'ko') => void; message: string }[]>([])

const active = ref<Card['id'][]>([])

eventBus.on('notifications:close', (card) => {
  active.value.push(card.id)
  modals.value.push({
    message: t('cab.notifications.ended'),
    callback: (res) => {
      active.value = []
      if (res === 'ok') {
        acknowledge(card)
      }
    }
  })
})

function closeModal(_: any, res: 'ok' | 'ko', modal: (typeof modals.value)[0]) {
  modals.value.splice(modals.value.indexOf(modal), 1)
  if (modal.callback) modal.callback(res)
}

function confirmDeletion(card: Card) {
  if (card.data.criticality !== 'ND') {
    active.value.push(card.id)
    modals.value.push({
      message: t('cab.notifications.delete', { event: card.titleTranslated }),
      callback: (res) => {
        active.value = []
        if (res === 'ok') {
          acknowledge(card)
        }
      }
    })
  } else acknowledge(card)
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
