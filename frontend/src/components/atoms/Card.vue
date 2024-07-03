<template>
  <div class="cab-card" :class="[orientation, color, { customColor: customColor }]">
    <div class="cab-card-outer"><slot name="outer"></slot></div>
    <div class="cab-card-inner"><slot></slot></div>
  </div>
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    orientation?: 'left' | 'right' | 'top' | 'bottom'
    color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error'
    customColor?: string
  }>(),
  { orientation: 'left', color: 'primary', customColor: undefined }
)
</script>
<style lang="scss">
.cab-card {
  --color-card-accent: var(--color-primary);
  background: var(--color-card-accent);
  border-radius: var(--radius-medium);
  display: flex;
  cursor: pointer;

  &.primary {
    --color-card-accent: var(--color-primary);
  }
  &.secondary {
    --color-card-accent: var(--color-secondary);
  }
  &.success {
    --color-card-accent: var(--color-success);
  }
  &.warning {
    --color-card-accent: var(--color-warning);
  }
  &.error {
    --color-card-accent: var(--color-error);
  }
  &.customColor {
    --color-card-accent: v-bind(props.customColor);
  }

  &.left {
    flex-direction: row;
  }
  &.right {
    flex-direction: row-reverse;
  }
  &.top {
    flex-direction: column;
  }
  &.bottom {
    flex-direction: column-reverse;
  }

  &-outer,
  &-inner {
    padding: var(--spacing-1);
  }

  &-outer {
    color: var(--color-text-inverted);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &-inner {
    --color-card-inner: var(--color-grey-100);
    border-radius: var(--radius-medium);
    border: calc(var(--unit) / 4) solid var(--color-card-accent);
    background-color: var(--color-card-inner);
    height: auto;
    flex: 1;
    transition: var(--duration);
    box-shadow:
      inset calc(var(--unit) * 0.5) calc(var(--unit) * 0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--color-card-inner), #000 20%),
      inset calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--color-card-inner), #ccc 20%);
  }
  &:hover .cab-card-inner,
  &.active .cab-card-inner {
    --color-card-inner: var(--color-grey-200);
  }
  &:focus .cab-card-inner,
  &:focus-within .cab-card-inner,
  &:active .cab-card-inner {
    --color-card-inner: var(--color-grey-300);
  }
}
</style>
