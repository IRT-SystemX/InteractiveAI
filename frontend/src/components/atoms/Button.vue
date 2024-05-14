<template>
  <button class="cab-btn" :class="[size, color, { icon }]" :type>
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
  --button-color: var(--color-primary);
  background: var(--button-color);
  color: var(--color-text-inverted);
  box-shadow:
    calc(var(--unit) * 0.5) calc(var(--unit) * 0.5) calc(var(--unit) * 1)
      color-mix(in srgb, var(--color-background), #000 15%),
    calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
      color-mix(in srgb, var(--color-background), #fff 15%);
  padding: var(--spacing-1);
  border-radius: var(--radius-circular);
  border: none;
  width: fit-content;

  &:active {
    box-shadow:
      inset calc(var(--unit) * 0.5) calc(var(--unit) * 0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--button-color), #000 15%),
      inset calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--button-color), #fff 15%);
  }

  &.small {
    height: calc(var(--unit) * 2);
    width: calc(var(--unit) * 3);
    --button-color: var(--color-grey-200);
    box-shadow:
      calc(var(--unit) * 0.25) calc(var(--unit) * 0.25) calc(var(--unit) * 0.5)
        color-mix(in srgb, var(--color-background), #000 15%),
      calc(var(--unit) * -0.25) calc(var(--unit) * -0.25) calc(var(--unit) * 0.5)
        color-mix(in srgb, var(--color-background), #fff 15%);
    color: var(--color-text);
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }

  &.primary {
    --button-color: var(--color-primary);
  }
  &.secondary {
    --button-color: var(--color-grey-300);
    color: var(--color-text);
  }
  &.success {
    --button-color: background: var(--color-success);
  }
  &.warning {
    --button-color: var(--color-warning);
  }
  &.error {
    --button-color: var(--color-error);
  }

  &.icon {
    aspect-ratio: 1;
    display: flex;
  }
}
</style>
