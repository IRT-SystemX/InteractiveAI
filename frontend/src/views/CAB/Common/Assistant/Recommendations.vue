<template>
  <Modal
    v-if="confirm"
    type="choice"
    data="Voulez-vous appliquer cette recommandation ?"
    @close="close"></Modal>
  <div class="flex flex-wrap flex-center-v flex-gap">
    <Settings />
    <Button v-for="button of buttons" :key="button">
      <slot name="buttons" :button="button">{{ button }}</slot>
    </Button>
  </div>
  <Card
    v-for="recommendation of recommendations"
    :key="recommendation"
    orientation="right"
    @click="selected = recommendation">
    <slot :recommendation="recommendation">
      <h1>{{ recommendation.title }}</h1>
    </slot>
    <template #outer><slot name="outer" :recommendation="recommendation"></slot></template>
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
import { Settings } from 'lucide-vue-next'
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
