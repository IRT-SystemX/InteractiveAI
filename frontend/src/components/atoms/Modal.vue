<template>
  <dialog ref="modal" class="cab-panel">
    {{ text }}
    <form method="dialog">
      <Button class="float-right" type="submit">{{ $t('button.ok') }}</Button>
    </form>
  </dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import eventBus from '@/plugins/eventBus'

import Button from './Button.vue'

const { t } = useI18n()

const modal = ref<HTMLDialogElement | null>(null)
const text = ref(t('modal.default'))

eventBus.on('modal', (message) => {
  modal.value && modal.value.showModal()
  text.value = message
})
</script>
<style lang="scss" scoped>
dialog {
  margin: auto;
  border: none;
  min-width: 25%;
  padding: var(--spacing-2);
  color: var(--color-text);

  &::backdrop {
    backdrop-filter: blur(2px);
  }
}
</style>
