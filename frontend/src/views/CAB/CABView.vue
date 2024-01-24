<template>
  <div class="cab-container">
    <Notifications class="cab-notifications" />
    <Context class="cab-context" />
    <Assistant class="cab-assistant" />
    <Timeline class="cab-timeline" />
  </div>
</template>
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
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
  gap: var(--spacing-1);
  grid-template-columns: [left-start] 320px [left-end] minmax(0, 1fr) [right-start] 320px [right-end];
  grid-template-rows: [top] minmax(0, 1fr) [middle] 240px [bottom];

  .cab-panel {
    display: flex;
    flex-direction: column;
  }

  .cab-notifications {
    grid-area: top / left-start / middle / left-end;

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
    grid-area: top / left-end / middle / right-start;
  }
  .cab-assistant {
    grid-area: top / right-start / middle / right-end;
  }
  .cab-timeline {
    grid-area: middle / left-start / bottom / right-end;
  }
}
</style>
