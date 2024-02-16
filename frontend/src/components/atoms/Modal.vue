<template>
  <div class="cab-modal-backdrop"></div>
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
</template>
<script setup lang="ts">
import type { UUID } from '@/types/formats'
import { uuid } from '@/utils/utils'

import Button from './Button.vue'

withDefaults(
  defineProps<{
    type: 'choice' | 'info'
    id?: UUID
  }>(),
  { id: uuid() }
)
defineEmits<{
  close: [id: UUID, res: 'ok' | 'ko']
}>()
</script>
<style lang="scss">
.cab-modal {
  min-width: 25%;
  margin: auto;
  padding: var(--spacing-2);
  color: var(--color-text);
  border: none;
  z-index: 3000;
  max-width: 90%;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
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
