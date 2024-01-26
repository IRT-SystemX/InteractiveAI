<template>
  <button class="cab-btn" :class="[size, color, { icon }]" :type="type">
    <slot></slot>
  </button>
</template>
<script setup lang="ts">
withDefaults(
  defineProps<{
    icon?: boolean
    size?: 'big' | 'medium' | 'small'
    color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
    type?: 'button' | 'submit' | 'reset'
  }>(),
  { size: 'medium', color: 'primary', type: 'button' }
)
</script>
<style lang="scss">
.cab-btn {
  cursor: pointer;
  background: var(--color-primary);
  color: var(--color-text-inverted);
  padding: var(--spacing-1);
  border-radius: var(--radius-circular);
  border: none;
  width: fit-content;

  &.small {
    height: calc(var(--unit) * 2);
    width: calc(var(--unit) * 3);
    background: var(--color-grey-200);
    color: var(--color-text);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }

  &.primary {
    background: var(--color-primary);
  }
  &.secondary {
    background: var(--color-secondary);
    color: var(--color-text);
  }
  &.success {
    background: var(--color-success);
  }
  &.warning {
    background: var(--color-warning);
  }
  &.error {
    background: var(--color-error);
  }

  &.icon {
    aspect-ratio: 1;
    display: flex;
  }
}
</style>
