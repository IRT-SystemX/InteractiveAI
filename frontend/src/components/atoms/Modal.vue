<template>
  <dialog ref="modal" class="cab-panel">
    {{ data }}
    <form method="dialog" class="cab-modal-buttons">
      <Button
        v-if="type === 'choice'"
        color="secondary"
        type="submit"
        @click="$emit('close', id, 'ko')">
        {{ $t('button.ko') }}
      </Button>
      <Button type="submit" @click="$emit('close', id, 'ok')">
        {{ $t('button.ok') }}
      </Button>
    </form>
  </dialog>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { onMounted } from 'vue'

import Button from './Button.vue'

withDefaults(
  defineProps<{
    type: 'choice' | 'info'
    id?: `${string}-${string}-${string}-${string}-${string}`
    data: string
  }>(),
  { id: crypto.randomUUID() }
)
defineEmits<{
  close: [id: `${string}-${string}-${string}-${string}-${string}`, res: 'ok' | 'ko']
}>()

const modal = ref<HTMLDialogElement>()

onMounted(() => {
  console.log(modal.value)
  modal.value && modal.value.showModal()
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
