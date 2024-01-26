<template>
  <div class="cab-container">
    <div class="cab-container-upper">
      <Notifications v-if="left > 120" class="cab-notifications" :style="{ width: `${left}px` }" />
      <div v-else class="cab-notifications cab-panel cab-section-placeholder">
        <h1>{{ $t('cab.notifications') }}</h1>
      </div>
      <div
        class="cab-handle left"
        draggable="true"
        :class="{ active: active === 'left' }"
        @drag="leftHandle"
        @dragstart="dragStart($event, 'left')"
        @dragend="dragEnd"
        @mousedown.middle="left = 320"
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
        @mousedown.middle="right = 320"
        @contextmenu.prevent="right = 320">
        <GripVertical width="16" />
      </div>
      <Assistant v-if="right > 120" class="cab-assistant" :style="{ width: `${right}px` }" />
      <div v-else class="cab-assistant cab-panel cab-section-placeholder">
        <h1>{{ $t('cab.assistant') }}</h1>
      </div>
    </div>
    <div
      class="cab-handle bottom"
      draggable="true"
      :class="{ active: active === 'bottom' }"
      @drag="bottomHandle"
      @dragstart="dragStart($event, 'bottom')"
      @dragend="dragEnd"
      @mousedown.middle="bottom = 240"
      @contextmenu.prevent="bottom = 240">
      <GripHorizontal height="16" />
    </div>
    <Timeline v-if="bottom > 96" class="cab-timeline" :style="{ height: `${bottom}px` }" />
    <div v-else class="cab-timeline cab-panel cab-section-placeholder">
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

  .cab-section-placeholder {
    text-align: center;
    &.cab-notifications,
    &.cab-assistant {
      writing-mode: vertical-rl;
    }
    &.cab-notifications {
      transform: rotate(180deg);
    }
  }

  .cab-notifications {
    max-width: 40vw;
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
    flex: 1;
    width: 0;
    grid-area: middle-start / center-start / middle-end / center-end;
  }
  .cab-assistant {
    max-width: 40vw;
    grid-area: middle-start / right-start / middle-end / right-end;
  }
  .cab-timeline {
    max-height: 60vh;
    grid-area: bottom-start / left-start / bottom-end / right-end;
  }
}
</style>
