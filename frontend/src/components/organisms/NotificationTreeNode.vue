<template>
  <div class="w-100">
    <Notification :criticality="card.data.criticality">
      <template #outer>
        <aside><slot name="outer"></slot></aside>
      </template>
      <div class="flex flex-center-y flex-gap">
        <ChevronDown
          v-if="children.length"
          :class="{ rotate: !showChildren }"
          @click="showChildren = !showChildren" />
        <div class="w-100">
          <header>
            <b><slot name="title"></slot></b>
            <aside><slot name="severity"></slot></aside>
          </header>
          <main><slot></slot></main>
          <footer><slot name="actions"></slot></footer>
        </div>
      </div>
    </Notification>
    <TransitionGroup name="fade">
      <div v-if="showChildren && children.length">
        <div v-for="child of children" :key="child.id" class="flex flex-gap mt-1">
          <CornerDownRight />
          <NotificationTreeNode :card="child">
            <template #outer>
              <aside><slot name="outer"></slot></aside>
            </template>
            <header>
              <b><slot name="title"></slot></b>
              <aside><slot name="severity"></slot></aside>
            </header>
            <main><slot></slot></main>
            <footer><slot name="actions"></slot></footer>
          </NotificationTreeNode>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>
<script setup lang="ts" generic="T extends Entity">
import { ChevronDown, CornerDownRight } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { useCardsStore } from '@/stores/cards'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'

import Notification from '../molecules/Notification.vue'

const props = defineProps<{ card: Card<T> }>()

const cardsStore = useCardsStore()

const children = computed(() =>
  cardsStore
    .cards(props.card.entityRecipients[0])
    .filter((child) => child.data.parent_event_id === props.card.processInstanceId)
)

const showChildren = ref(true)
</script>
<style lang="scss">
.lucide {
  transition: var(--duration);
  &.rotate {
    transform: rotate(-90deg);
  }
}
</style>
