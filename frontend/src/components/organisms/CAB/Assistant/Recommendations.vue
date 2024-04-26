<template>
  <Modal v-if="confirm" type="choice" @close="close">
    <slot name="modal" :selected>
      <i18n-t scope="global" keypath="recommendations.modal">
        <template #recommendation>
          <strong style="color: var(--color-primary)">
            {{ selected?.title }}
          </strong>
        </template>
      </i18n-t>
    </slot>
  </Modal>
  <div class="flex flex-wrap flex-center-y flex-gap">
    <div v-for="button of buttons" :key="button" class="cab-recommendation-kpi">
      <Button>
        <slot name="buttons" :button>{{ $t(button) }}</slot>
      </Button>
      <Button
        color="secondary"
        class="cab-recommendation-kpi-actions flex flex-gap"
        @click="closeKpi(button)">
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
    <template #outer>
      <slot name="outer" :recommendation>
        <ThumbsDown color="var(--color-grey-100)" :size="16" @click="downvote(recommendation)" />
      </slot>
    </template>
  </Card>
  <div class="flex flex-end flex-gap">
    <slot name="button"></slot>
    <Button v-if="selected" @click="confirm = true">
      {{ $t('button.apply') }}
    </Button>
  </div>
  <div v-if="selected" class="cab-recommendation-description">
    <h2>{{ $t('recommendations.description') }}</h2>
    <div :class="{ collapsed: collapsed && !details }">
      {{ selected.description }}
    </div>
    <Button v-if="collapsed" class="float-right" @click="details = !details">
      {{ $t('recommendations.description.more', { sign: details ? '-' : '+' }) }}
    </Button>
  </div>
  <slot name="footer"></slot>
</template>
<script setup lang="ts" generic="T extends Entity">
import { CircleX, ThumbsDown } from 'lucide-vue-next'
import { onBeforeMount, ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import Card from '@/components/atoms/Card.vue'
import Modal from '@/components/atoms/Modal.vue'
import type { Entity } from '@/types/entities'
import type { Recommendation } from '@/types/services'

const props = withDefaults(
  defineProps<{ buttons: string[]; recommendations: Recommendation<T>[]; collapsed?: boolean }>(),
  { collapsed: false }
)
const emit = defineEmits<{
  'update:recommendations': [recommendation: Recommendation<T>[]]
  selected: [recommendation: Recommendation<T>]
}>()

const selected = ref<Recommendation<T>>()
const buttons = ref<typeof props.buttons>()
const confirm = ref(false)
const details = ref(false)

onBeforeMount(() => {
  buttons.value = props.buttons
})

function close(_: any, res: 'ok' | 'ko') {
  if (res === 'ok') emit('selected', selected.value!)
  confirm.value = false
}

function closeKpi(kpi: (typeof props)['buttons'][number]) {
  buttons.value?.splice(buttons.value.indexOf(kpi), 1)
}

function downvote(recommendation: Recommendation<T>) {
  emit(
    'update:recommendations',
    props.recommendations.filter((rec) => rec.title !== recommendation.title)
  )
  console.log(recommendation) // TODO
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
    }
  }
  &-description .collapsed {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
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
