<template>
  <main class="cab-event">
    <SVG src="logo" fill="var(--color-primary)" :width="56" class="self-center"></SVG>
    <div>
      <SpeechBubble>
        <strong :style="{ color: `var(--color-${severityToColor(card.severity)})` }">
          {{ card.titleTranslated }}
        </strong>
        détectée. Souhaitez-vous de l'aide pour traiter l'événement ?
      </SpeechBubble>
    </div>
    <div class="row">
      <Button type="button" @click="askRecommendations">Consulter les recommendations</Button>
      <Info
        fill="var(--color-grey-600)"
        stroke="var(--color-background)"
        :width="20"
        class="ml-1" />
    </div>
    <div class="row">
      <Button type="button" color="secondary">Utiliser l'outil d'étude</Button>
      <Info
        fill="var(--color-grey-600)"
        stroke="var(--color-background)"
        :width="20"
        class="ml-1" />
    </div>
  </main>
</template>
<script setup lang="ts">
import { Info } from 'lucide-vue-next'
import { useRoute } from 'vue-router'

import { sendTrace } from '@/api/services'
import Button from '@/components/atoms/Button.vue'
import SpeechBubble from '@/components/atoms/SpeechBubble.vue'
import SVG from '@/components/atoms/SVG.vue'
import eventBus from '@/plugins/eventBus'
import type { Card } from '@/types/cards'
import type { Entity } from '@/types/entities'
import type { Metadata } from '@/types/entities/RTE'
import { severityToColor } from '@/utils/utils'

defineProps<{ card: Card<Metadata> }>()

const route = useRoute()

function askRecommendations() {
  sendTrace({
    data: {},
    use_case: route.params.entity as Entity,
    step: 'ASKFORHELP'
  })
  eventBus.emit('assistant:tab', 2)
}
</script>
<style lang="scss">
.cab-event {
  box-sizing: border-box;
  background: #fff;

  display: flex;
  flex-direction: column;
  font-size: 14px;

  h1 {
    font-size: 20px;
    margin: 0;
    margin-bottom: 8px;
  }
  main {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .logo {
    width: 58px;
    align-self: center;
  }
  .icon {
    width: 16px;
    margin-left: 8px;
  }
  .row {
    display: flex;
    align-items: center;
  }
}
</style>
