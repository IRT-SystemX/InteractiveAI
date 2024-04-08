<template>
  <Modal v-if="confirm" type="choice" @close="close">
    <slot name="modal" :selected>
      <i18n-t scope="global" keypath="recommendations.modal">
        <template #recommendation>
          <strong style="color: var(--color-primary)">
            {{ selected.title }}
          </strong>
        </template>
      </i18n-t>
    </slot>
  </Modal>
  <div class="flex flex-wrap flex-center-y flex-gap">
    <div v-for="button of buttons" :key="button" class="cab-recommendation-kpi">
      <Button>
        <slot name="buttons" :button>{{ button }}</slot>
      </Button>
      <Button color="secondary" class="cab-recommendation-kpi-actions flex flex-gap">
        <ThumbsDown color="var(--color-grey-100)" :size="16" />
        <CircleX color="var(--color-grey-100)" :size="16" />
      </Button>
    </div>
  </div>
  <Card
    v-for="recommendation of recommendations"
    :key="recommendation?.title"
    class="cab-recommendation"
    :class="{ selected: recommendation?.title === selected?.title }"
    orientation="right"
    @click="selected = recommendation">
    <slot :recommendation>
      <h1>{{ recommendation.title }}</h1>
    </slot>
    <template #outer><slot name="outer" :recommendation></slot></template>
  </Card>
  <Button v-if="selected" class="self-end" @click="confirm = true">
    {{ $t('button.apply') }}
  </Button>
  <div v-if="selected">
    <h2>{{ $t('recommendations.description') }}</h2>
    {{ selected.description }}
  </div>
</template>
<script setup lang="ts">
import { CircleX, ThumbsDown } from 'lucide-vue-next'
import { ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import Card from '@/components/atoms/Card.vue'
import Modal from '@/components/atoms/Modal.vue'

defineProps<{ buttons: any[]; recommendations: any[] }>()
const emit = defineEmits<{ selected: [recommendation: any] }>()

const selected = ref<any>()
const confirm = ref(false)

function close(_: any, res: 'ok' | 'ko') {
  if (res === 'ok') emit('selected', selected.value)
  confirm.value = false
}
</script>
<style lang="scss">
.cab-recommendation {
  scroll-snap-align: start;
  .cab-card-outer {
    width: 0;
    color: #fff0;
    max-width: fit-content;
    transition: var(--duration);

    .lucide:hover {
      fill: var(--color-background);
    }
  }
  &.selected {
    z-index: 2500;
  }
  &.selected .cab-card-inner {
    background: var(--color-grey-200);
  }
  &-kpi {
    position: relative;
    &:hover .cab-recommendation-kpi-actions {
      position: absolute;
      right: 0;
      bottom: 0;
      transform: translateY(80%);
      display: flex;
      z-index: 100;
    }
    &-actions {
      display: none;

      svg:hover {
        fill: var(--color-grey-100);
        stroke: var(--color-grey-300);
      }
    }
  }
  &:hover .cab-card-outer,
  &.selected .cab-card-outer {
    color: #fff;
    width: 40px;
  }
  .cab-card-inner {
    display: flex;
    justify-content: space-between;
  }
}
</style>
