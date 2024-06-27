<template>
  <div class="w-100">
    <div class="flex">
      <CornerDownRight v-if="isChild" />
      <Notification
        :criticality="card.data.criticality"
        class="flex-1"
        :class="{ active: appStore._card?.id === card.id }"
        @click.stop="selected(card)">
        <template #outer>
          <aside><slot name="outer" :card></slot></aside>
        </template>
        <div class="flex flex-center-y flex-gap">
          <ChevronDown
            v-if="children.length"
            :class="{ rotate: !showChildren }"
            @click.stop="showChildren = !showChildren" />
          <div class="w-100">
            <header :style="{ color: card.read ? 'var(--color-grey-600)' : undefined }">
              <b>
                <slot name="title" :card></slot>
              </b>
              <aside><slot name="severity" :card></slot></aside>
            </header>
            <main><slot :card></slot></main>
            <footer><slot name="actions" :card></slot></footer>
          </div>
        </div>
      </Notification>
    </div>
    <template v-if="showChildren && children.length">
      <div v-for="child of children" :key="child.id" class="flex flex-gap mt-1">
        <NotificationTreeNode :card="child" :grouped="false" :is-child="true">
          <template #outer>
            <slot name="outer" :card="child"></slot>
          </template>
          <template #title>
            <slot name="title" :card="child"></slot>
          </template>
          <template #severity>
            <slot name="severity" :card="child"></slot>
          </template>
          <template #default>
            <slot :card="child"></slot>
          </template>
          <template #actions>
            <slot name="actions" :card="child"></slot>
          </template>
        </NotificationTreeNode>
      </div>
    </template>
  </div>
</template>
<script setup lang="ts" generic="E extends Entity">
import { ChevronDown, CornerDownRight } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { useAppStore } from '@/stores/app'
import { useCardsStore } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

import Notification from '../molecules/Notification.vue'

const props = defineProps<{
  card: Card<E>
  isChild: boolean
  hasBeenAcknowledged?: boolean
  selection?: (card: Card<E>) => void
}>()

const cardsStore = useCardsStore()
const appStore = useAppStore()

const showChildren = ref(true)

const children = computed(() =>
  cardsStore
    .cards(props.card.entityRecipients[0], props.hasBeenAcknowledged)
    .filter((card) => card.data.parent_event_id === props.card.processInstanceId)
)

function selected(card: Card<E>) {
  if (props.selection) props.selection(card)
  else {
    card.read = true
    appStore._card = card
  }
}
</script>
<style lang="scss">
.lucide {
  transition: var(--duration);
  &.rotate {
    transform: rotate(-90deg);
  }
}
</style>
