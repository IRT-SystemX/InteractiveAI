<template>
  <div class="w-100">
    <div class="flex">
      <CornerDownRight v-if="isChild" />
      <Notification
        :criticality="card.data.criticality"
        class="flex-1"
        @click.stop="selected(card)">
        <template #outer>
          <aside><slot name="outer" :card="card"></slot></aside>
        </template>
        <div class="flex flex-center-y flex-gap">
          <ChevronDown
            v-if="card.children?.length"
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
    </div>
    <div v-if="showChildren && card.children.length">
      <div v-for="child of card.children" :key="child.id" class="flex flex-gap mt-1">
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
    </div>
  </div>
</template>
<script setup lang="ts" generic="E extends Entity">
import { ChevronDown, CornerDownRight } from 'lucide-vue-next'
import { ref } from 'vue'

import eventBus from '@/plugins/eventBus'
import type { CardTree } from '@/types/cards'
import type { Entity } from '@/types/entities'

import Notification from '../molecules/Notification.vue'

const props = defineProps<{
  card: CardTree<E>
  isChild: boolean
}>()
const read = ref(false)

const showChildren = ref(true)

function selected(card: CardTree<E>) {
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
