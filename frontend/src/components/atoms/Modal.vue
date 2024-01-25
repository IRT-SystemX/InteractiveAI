<template>
  <dialog v-for="modal in modals" ref="modalHTML" :key="modal.id" class="cab-panel">
    {{ modal.data }}
    <form method="dialog" class="cab-modal-buttons">
      <Button
        v-if="modal.type === 'choice'"
        color="secondary"
        type="submit"
        @click="eventBus.emit('modal:close', { id: modal.id, res: 'ko' })">
        {{ $t('button.ko') }}
      </Button>
      <Button type="submit" @click="eventBus.emit('modal:close', { id: modal.id, res: 'ok' })">
        {{ $t('button.ok') }}
      </Button>
    </form>
  </dialog>
</template>
<script setup lang="ts">
import { nextTick, ref } from 'vue'

import eventBus from '@/plugins/eventBus'

import Button from './Button.vue'

const modalHTML = ref<HTMLDialogElement[]>([])
const modals = ref<
  {
    id: `${string}-${string}-${string}-${string}-${string}`
    data: string
    type: 'choice' | 'info'
  }[]
>([])

eventBus.on('modal:open', (message) => {
  const index = modals.value.push({ id: crypto.randomUUID(), ...message })
  nextTick(() => {
    modalHTML.value && modalHTML.value[index - 1].showModal()
  })
})
</script>
<style lang="scss" scoped>
dialog {
  margin: auto;
  border: none;
  min-width: 25%;
  padding: var(--spacing-2);
  color: var(--color-text);

  .cab-modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-1);
  }

  &::backdrop {
    backdrop-filter: blur(2px);
  }
}
</style>
