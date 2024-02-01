<template>
  <div class="cab-modal-backdrop">
    <dialog ref="modal" open class="cab-panel cab-modal">
      <slot></slot>
      <div class="cab-modal-buttons">
        <Button
          v-if="type === 'choice'"
          color="secondary"
          type="button"
          @click="$emit('close', id, 'ko')">
          {{ $t('button.no') }}
        </Button>
        <Button type="button" @click="$emit('close', id, 'ok')">
          {{ type === 'choice' ? $t('button.yes') : $t('button.ok') }}
        </Button>
      </div>
    </dialog>
  </div>
</template>
<script setup lang="ts">
import Button from './Button.vue'

withDefaults(
  defineProps<{
    type: 'choice' | 'info'
    id?: `${string}-${string}-${string}-${string}-${string}`
  }>(),
  { id: crypto.randomUUID() }
)
defineEmits<{
  close: [id: `${string}-${string}-${string}-${string}-${string}`, res: 'ok' | 'ko']
}>()
</script>
<style lang="scss">
.cab-modal {
  min-width: 25%;
  margin: auto;
  padding: var(--spacing-2);
  color: var(--color-text);
  border: none;
  z-index: 2000;
  max-width: 90%;
  .cab-modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-1);
  }

  &-backdrop {
    z-index: 2000;
    position: absolute;
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(2px);
    background: #72727233;
    top: 0;
    left: 0;
  }
}
</style>
