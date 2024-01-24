<template>
  <div class="cab-container">
    <Notifications class="cab-notifications" />
    <div
      class="cab-handle left"
      draggable="true"
      :class="{ active: active === 'left' }"
      @drag="leftHandle"
      @dragstart="dragStart($event, 'left')"
      @dragend="dragEnd"
      @contextmenu.prevent="left = 320">
      <GripVertical width="16" />
    </div>
    <Context class="cab-context" />
    <div
      class="cab-handle right"
      draggable="true"
      :class="{ active: active === 'right' }"
      @drag="rightHandle"
      @dragstart="dragStart($event, 'right')"
      @dragend="dragEnd"
      @contextmenu.prevent="right = 320">
      <GripVertical width="16" />
    </div>
    <Assistant class="cab-assistant" />
    <div
      class="cab-handle bottom"
      draggable="true"
      :class="{ active: active === 'bottom' }"
      @drag="bottomHandle"
      @dragstart="dragStart($event, 'bottom')"
      @dragend="dragEnd"
      @contextmenu.prevent="bottom = 240">
      <GripHorizontal height="16" />
    </div>
    <Timeline class="cab-timeline" />
  </div>
</template>
<script setup lang="ts">
import { GripHorizontal, GripVertical } from 'lucide-vue-next'
import { defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute } from 'vue-router'

import { toggleMode } from '@/plugins/colorMode'
import { useCardsStore } from '@/stores/cards'
import { Entities, type Entity } from '@/types/entities'

let Assistant = defineAsyncComponent(() => import(`./${route.params.entity}/Assistant.vue`))
let Context = defineAsyncComponent(() => import(`./${route.params.entity}/Context.vue`))
let Notifications = defineAsyncComponent(() => import(`./${route.params.entity}/Notifications.vue`))
let Timeline = defineAsyncComponent(() => import(`./${route.params.entity}/Timeline.vue`))

const route = useRoute()
const { locale } = useI18n()
const cardsStore = useCardsStore()

const left = ref(320)
const right = ref(320)
const bottom = ref(240)
const active = ref('')

function dragStart(ev: DragEvent, value: 'left' | 'right' | 'bottom') {
  active.value = value
  const img = new Image()
  ev.dataTransfer!.setDragImage(img, 0, 0)
}

function dragEnd() {
  active.value = ''
}

function leftHandle(ev: DragEvent) {
  left.value = ev.clientX ? ev.clientX - 8 : left.value
}

function rightHandle(ev: DragEvent) {
  right.value = ev.clientX ? document.body.clientWidth - ev.clientX - 8 : right.value
}

function bottomHandle(ev: DragEvent) {
  bottom.value = ev.clientY ? document.body.clientHeight - ev.clientY - 8 : bottom.value
}

setup(route.params.entity as Entity)

function setup(entity: Entity) {
  cardsStore.getCards(
    route.params.entity as Entity,
    Entities[route.params.entity as Entity].hydrated
  )
  locale.value = `${locale.value.slice(0, 2)}-${entity}`
  toggleMode(entity)

  Assistant = defineAsyncComponent(() => import(`./${route.params.entity}/Assistant.vue`))
  Context = defineAsyncComponent(() => import(`./${route.params.entity}/Context.vue`))
  Notifications = defineAsyncComponent(() => import(`./${route.params.entity}/Notifications.vue`))
  Timeline = defineAsyncComponent(() => import(`./${route.params.entity}/Timeline.vue`))
}

onBeforeRouteUpdate((to) => {
  setup(to.params.entity as Entity)
})

onBeforeRouteLeave(() => {
  toggleMode('auto')
  cardsStore.closeCards()
})
</script>
<style lang="scss">
.cab-container {
  padding: var(--spacing-1);
  display: grid;
  height: calc(100vh - 60px);
  transition: 0.1s;
  grid-template-columns:
    [left-start] clamp(64px, calc(v-bind(left) * 1px), 40%) [left-end]
    var(--spacing-1)
    [center-start] minmax(0, 1fr) [center-end]
    var(--spacing-1)
    [right-start] clamp(64px, calc(v-bind(right) * 1px), 40%) [right-end];
  grid-template-rows:
    [middle-start] minmax(0, 1fr) [middle-end]
    var(--spacing-1)
    [bottom-start] clamp(96px, calc(v-bind(bottom) * 1px), 60%) [bottom-end];

  .cab-handle {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-medium);
    transition: var(--duration);
    &.active {
      background: var(--color-grey-600);
    }
    &.left,
    &.right {
      cursor: col-resize;
      flex-direction: column;
    }
    &.left {
      grid-area: middle-start / left-end / middle-end / center-start;
    }
    &.right {
      grid-area: middle-start / center-end / middle-end / right-start;
    }
    &.bottom {
      grid-area: middle-end / left-start / bottom-start / right-end;
      cursor: row-resize;
    }
  }

  .cab-panel {
    display: flex;
    flex-direction: column;
  }

  .cab-notifications {
    grid-area: middle-start / left-start / middle-end / left-end;

    .card-container {
      overflow: auto;
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
    }

    &-main {
      height: 67%;
    }

    &-sub {
      height: 33%;
    }
  }
  .cab-context {
    grid-area: middle-start / center-start / middle-end / center-end;
  }
  .cab-assistant {
    grid-area: middle-start / right-start / middle-end / right-end;
  }
  .cab-timeline {
    grid-area: bottom-start / left-start / bottom-end / right-end;
  }
}
</style>
