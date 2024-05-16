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
  --color-button-background: var(--color-primary);
  background: var(--color-button-background);
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
        color-mix(in srgb, var(--color-button-background), #000 15%),
      inset calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--color-button-background), #fff 15%);
  }

  &.small {
    height: calc(var(--unit) * 2);
    width: calc(var(--unit) * 3);
    --color-button-background: var(--color-grey-200);
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
    --color-button-background: var(--color-primary);
  }
  &.secondary {
    --color-button-background: var(--color-grey-300);
    color: var(--color-text);
  }
  &.success {
    --color-button-background: background: var(--color-success);
  }
  &.warning {
    --color-button-background: var(--color-warning);
  }
  &.error {
    --color-button-background: var(--color-error);
  }

  &.icon {
    aspect-ratio: 1;
    display: flex;
  }
}
</style>
