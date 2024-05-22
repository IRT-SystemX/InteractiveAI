<template>
  <div class="cab-container">
    <div class="cab-container-upper">
      <div v-if="appStore.panels.left" ref="leftPanel" style="width: 320px; max-width: 40vw">
        <Notifications class="cab-notifications" />
      </div>
      <div v-else class="cab-notifications cab-panel cab-section-placeholder">
        <h1>{{ $t('cab.notifications') }}</h1>
      </div>
      <div
        class="cab-handle left"
        draggable="true"
        :class="{ active: active === 'left' }"
        @drag="resize($event, 'left')"
        @dragstart="dragStart($event, 'left')"
        @dragend="dragEnd"
        @click="appStore.panels.left = !appStore.panels.left"
        @mousedown.middle="reset('left')"
        @contextmenu.prevent="reset('left')">
        <GripVertical width="16" />
      </div>
      <main class="flex flex-col cab-context">
        <Context />
      </main>
      <div
        class="cab-handle right"
        draggable="true"
        :class="{ active: active === 'right' }"
        @drag="resize($event, 'right')"
        @dragstart="dragStart($event, 'right')"
        @dragend="dragEnd"
        @click="appStore.panels.right = !appStore.panels.right"
        @mousedown.middle="reset('right')"
        @contextmenu.prevent="reset('right')">
        <GripVertical width="16" />
      </div>
      <div v-if="appStore.panels.right" ref="rightPanel" style="width: 320px; max-width: 40vw">
        <Assistant class="cab-assistant" />
      </div>
      <div v-else class="cab-assistant cab-panel cab-section-placeholder">
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
      @click="appStore.panels.bottom = !appStore.panels.bottom"
      @mousedown.middle="reset('bottom')"
      @contextmenu.prevent="reset('bottom')">
      <GripHorizontal height="16" />
    </div>
    <div v-if="appStore.panels.bottom" ref="bottomPanel" style="height: 240px; max-height: 60vh">
      <Timeline class="cab-timelines" />
    </div>
    <div v-else class="cab-timelines cab-panel cab-section-placeholder">
      <h1>{{ $t('cab.timeline') }}</h1>
    </div>
  </div>
</template>
<script setup lang="ts">
import { GripHorizontal, GripVertical } from 'lucide-vue-next'
import { defineAsyncComponent, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute } from 'vue-router'

import Loading from '@/components/atoms/Loading.vue'
import DefaultNotifications from '@/components/organisms/CAB/Notifications.vue'
import { toggleMode } from '@/plugins/colorMode'
import eventBus from '@/plugins/eventBus'
import { useAppStore } from '@/stores/app'
import { useCardsStore } from '@/stores/cards'
import { type Entity } from '@/types/entities'

import DefaultAssistant from './CAB/DefaultAssistant.vue'
import DefaultContext from './CAB/DefaultContext.vue'
import DefaultTimeline from './CAB/DefaultTimeline.vue'

let Assistant = defineAsyncComponent({
  loader: () => import(`./${route.params.entity}/Assistant.vue`),
  loadingComponent: Loading,
  errorComponent: DefaultAssistant
})
let Context = defineAsyncComponent({
  loader: () => import(`./${route.params.entity}/Context.vue`),
  loadingComponent: Loading,
  errorComponent: DefaultContext
})
let Notifications = defineAsyncComponent({
  loader: () => import(`./${route.params.entity}/Notifications.vue`),
  loadingComponent: Loading,
  errorComponent: DefaultNotifications
})
let Timeline = defineAsyncComponent({
  loader: () => import(`./${route.params.entity}/Timeline.vue`),
  loadingComponent: Loading,
  errorComponent: DefaultTimeline
})

const route = useRoute()
const { locale } = useI18n()
const cardsStore = useCardsStore()
const appStore = useAppStore()

const leftPanel = ref<HTMLDivElement>()
const rightPanel = ref<HTMLDivElement>()
const bottomPanel = ref<HTMLDivElement>()
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
          appStore.panels.left = ev.clientX > 120
          leftPanel.value!.style.width = ev.clientX - 8 + 'px'
        })
        break
      case 'right':
        window.requestAnimationFrame(() => {
          appStore.panels.right = width - ev.clientX - 16 > 120
          rightPanel.value!.style.width = width - ev.clientX - 16 + 'px'
        })
        break

      case 'bottom':
        window.requestAnimationFrame(() => {
          appStore.panels.bottom = height - ev.clientY - 16 > 96
          bottomPanel.value!.style.height = height - ev.clientY - 16 + 'px'
        })
        break
    }
  }
}

function reset(panel: 'left' | 'right' | 'bottom') {
  switch (panel) {
    case 'left':
      appStore.panels.left = true
      leftPanel.value!.style.width = 320 + 'px'
      break
    case 'right':
      appStore.panels.right = true
      rightPanel.value!.style.width = 320 + 'px'
      break
    case 'bottom':
      appStore.panels.bottom = true
      bottomPanel.value!.style.height = 240 + 'px'
      break
  }
}

setup(route.params.entity as Entity)

function setup(entity: Entity) {
  cardsStore.subscribe(entity)
  locale.value = `${locale.value.slice(0, 2)}-${entity}`
  toggleMode(entity)

  Assistant = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Assistant.vue`))
  Context = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Context.vue`))
  Notifications = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Notifications.vue`))
  Timeline = defineAsyncComponent(() => import(`../entities/${entity}/CAB/Timeline.vue`))
}

function remove() {
  eventBus.off('graph:showTooltip')
  cardsStore.unsubscribe()
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
  padding-top: 0;
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
      background: var(--color-grey-200);
      box-shadow:
        calc(var(--unit) * 0.25) calc(var(--unit) * 0.25) calc(var(--unit) * 0.5)
          color-mix(in srgb, var(--color-grey-200), #000 20%),
        calc(var(--unit) * -0.25) calc(var(--unit) * -0.25) calc(var(--unit) * 0.5)
          color-mix(in srgb, var(--color-grey-200), #ccc 20%);
    }
    &.active {
      box-shadow:
        inset calc(var(--unit) * 0.25) calc(var(--unit) * 0.25) calc(var(--unit) * 0.5)
          color-mix(in srgb, var(--color-background), #000 20%),
        inset calc(var(--unit) * -0.25) calc(var(--unit) * -0.25) calc(var(--unit) * 0.5)
          color-mix(in srgb, var(--color-background), #ccc 20%);
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
  .cab-context {
    flex: 1;
    width: 100%;
  }
}
</style>
