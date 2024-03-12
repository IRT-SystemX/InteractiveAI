<template>
  <div class="w-100">
    <Notification :criticality="card.data.criticality" @click.stop="selected(card)">
      <template #outer>
        <aside><slot name="outer" :card="card"></slot></aside>
      </template>
      <div class="flex flex-center-y flex-gap">
        <ChevronDown
          v-if="children.length"
          :class="{ rotate: !showChildren }"
          @click.stop="showChildren = !showChildren" />
        <div class="w-100">
          <header :style="{ color: read ? 'var(--color-grey-600)' : undefined }">
            <b>
              <slot name="title" :card="card"></slot>
            </b>
            <aside><slot name="severity" :card="card"></slot></aside>
          </header>
          <main><slot :card="card"></slot></main>
          <footer><slot name="actions" :card="card"></slot></footer>
        </div>
      </div>
    </Notification>
    <div v-if="showChildren && children.length">
      <div v-for="child of children" :key="child.id" class="flex flex-gap mt-1">
        <CornerDownRight />
        <NotificationTreeNode :card="child">
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
    </div>
  </div>
</template>
<script setup lang="ts" generic="T extends Entity">
import { ChevronDown, CornerDownRight } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

import Notification from '../molecules/Notification.vue'

const props = defineProps<{ card: Card<T> }>()
const read = ref(false)

const cardsStore = useCardsStore()

const children = computed(() =>
  cardsStore
    .cards(props.card.entityRecipients[0])
    .filter((child) => child.data.parent_event_id === props.card.processInstanceId)
)

const showChildren = ref(true)

function selected(card: Card<T>) {
  read.value = true
  // @ts-ignore
  eventBus.emit(`assistant:selected:${props.card.entityRecipients[0]}`, card)
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
