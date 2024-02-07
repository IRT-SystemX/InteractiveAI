<template>
  <div class="cab-container">
    <div class="cab-container-upper">
      <div v-show="left" ref="leftPanel" style="width: 320px; max-width: 40vw; transition: 0.05s">
        <Notifications class="cab-notifications" />
      </div>
      <div v-show="!left" class="cab-notifications cab-panel cab-section-placeholder">
        <h1>{{ $t('cab.notifications') }}</h1>
      </div>
      <div
        class="cab-handle left"
        draggable="true"
        :class="{ active: active === 'left' }"
        @drag="resize($event, 'left')"
        @dragstart="dragStart($event, 'left')"
        @dragend="dragEnd"
        @click="left = !left"
        @mousedown.middle="reset('left')"
        @contextmenu.prevent="reset('left')">
        <GripVertical width="16" />
      </div>
      <Context class="cab-context" />
      <div
        class="cab-handle right"
        draggable="true"
        :class="{ active: active === 'right' }"
        @drag="resize($event, 'right')"
        @dragstart="dragStart($event, 'right')"
        @dragend="dragEnd"
        @click="right = !right"
        @mousedown.middle="reset('right')"
        @contextmenu.prevent="reset('right')">
        <GripVertical width="16" />
      </div>
      <div v-show="right" ref="rightPanel" style="width: 320px; max-width: 40vw; transition: 0.05s">
        <Assistant class="cab-assistant" />
      </div>
      <div v-show="!right" class="cab-assistant cab-panel cab-section-placeholder">
        <h1>{{ $t('cab.assistant') }}</h1>
      </div>
    </div>
    <div
      class="cab-handle bottom"
      draggable="true"
      :class="{ active: active === 'bottom' }"
      @drag="resize($event, 'bottom')"
      @dragstart="dragStart($event, 'bottom')"
      @dragend="dragEnd"
      @click="bottom = !bottom"
      @mousedown.middle="reset('bottom')"
      @contextmenu.prevent="reset('bottom')">
      <GripHorizontal height="16" />
    </div>
    <div
      v-show="bottom"
      ref="bottomPanel"
      style="height: 240px; max-height: 60vh; transition: 0.05s">
      <Timeline class="cab-timelines" />
    </div>
    <div v-show="!bottom" class="cab-timelines cab-panel cab-section-placeholder">
      <h1>{{ $t('cab.timeline') }}</h1>
    </div>
  </div>
</template>
<script setup lang="ts">
import { GripHorizontal, GripVertical } from 'lucide-vue-next'
import { defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute } from 'vue-router'

import { toggleMode } from '@/plugins/colorMode'
import eventBus from '@/plugins/eventBus'
import { useCardsStore } from '@/stores/cards'
import { EntitiesArray, type Entity } from '@/types/entities'

let Assistant = defineAsyncComponent(() => import(`./${route.params.entity}/Assistant.vue`))
let Context = defineAsyncComponent(() => import(`./${route.params.entity}/Context.vue`))
let Notifications = defineAsyncComponent(() => import(`./${route.params.entity}/Notifications.vue`))
let Timeline = defineAsyncComponent(() => import(`./${route.params.entity}/Timeline.vue`))

const route = useRoute()
const { locale } = useI18n()
const cardsStore = useCardsStore()

const leftPanel = ref<HTMLDivElement | null>(null)
const left = ref(true)
const rightPanel = ref<HTMLDivElement | null>(null)
const right = ref(true)
const bottomPanel = ref<HTMLDivElement | null>(null)
const bottom = ref(true)
const active = ref('')

function dragStart(ev: DragEvent, value: 'left' | 'right' | 'bottom') {
  active.value = value
  const img = new Image()
  ev.dataTransfer!.setDragImage(img, 0, 0)
}

function dragEnd() {
  active.value = ''
}

function resize(ev: DragEvent, panel: 'left' | 'right' | 'bottom') {
  if (ev.clientX && ev.clientY) {
    const width = document.body.clientWidth
    const height = document.body.clientHeight
    switch (panel) {
      case 'left':
        window.requestAnimationFrame(() => {
          leftPanel.value!.style.width = ev.clientX - 8 + 'px'
          left.value = ev.clientX > 120
        })
        break
      case 'right':
        window.requestAnimationFrame(() => {
          rightPanel.value!.style.width = width - ev.clientX - 16 + 'px'
          right.value = width - ev.clientX - 16 > 120
        })
        break

      case 'bottom':
        window.requestAnimationFrame(() => {
          bottomPanel.value!.style.height = height - ev.clientY - 16 + 'px'
          bottom.value = height - ev.clientY - 16 > 96
        })
        break
    }
  }
}

function reset(panel: 'left' | 'right' | 'bottom') {
  switch (panel) {
    case 'left':
      leftPanel.value!.style.width = 320 + 'px'
      left.value = true
      break
    case 'right':
      rightPanel.value!.style.width = 320 + 'px'
      right.value = true
      break
    case 'bottom':
      bottomPanel.value!.style.height = 240 + 'px'
      bottom.value = true
      break
  }
}

setup(route.params.entity as Entity)

function setup(entity: Entity) {
  cardsStore.getCards(entity)
  locale.value = `${locale.value.slice(0, 2)}-${entity}`
  toggleMode(entity)

  Assistant = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Assistant.vue`))
  Context = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Context.vue`))
  Notifications = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Notifications.vue`))
  Timeline = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Timeline.vue`))
}

function remove() {
  eventBus.off('assistant:tab')
  for (const entity of EntitiesArray) eventBus.off(`assistant:selected:${entity}`)
  eventBus.off('tabs:selected')
  eventBus.off('graph:showTooltip')
  cardsStore.closeCards()
}

onBeforeRouteUpdate((to) => {
  remove()
  setup(to.params.entity as Entity)
})

onBeforeRouteLeave(() => {
  remove()
  toggleMode('auto')
})
</script>
<style lang="scss">
.cab-container {
  padding: var(--spacing-1);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  width: 100vw;

  &-upper {
    display: flex;
    flex: 1;
    height: 0;
  }

  .cab-handle {
    display: flex;
    z-index: 1000;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-medium);
    transition: var(--duration);
    &:hover {
      background: var(--color-grey-300);
    }
    &.active {
      background: var(--color-grey-400);
    }
    &.left,
    &.right {
      cursor: col-resize;
      flex-direction: column;
    }
    &.bottom {
      cursor: row-resize;
    }
  }

  .cab-notifications,
  .cab-context,
  .cab-assistant,
  .cab-timelines {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .cab-section-placeholder {
    text-align: center;
    &.cab-timelines {
      height: 40px;
    }
    &.cab-notifications,
    &.cab-assistant {
      writing-mode: vertical-rl;
      width: 40px;
    }
    &.cab-notifications h1 {
      transform: rotate(180deg);
    }
  }

  .cab-notifications {
    resize: horizontal;

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

    &-main {
      height: 67%;
    }

    &-sub {
      height: 33%;
    }
  }
  .cab-context {
    flex: 1;
    width: 0;
  }
}
</style>
