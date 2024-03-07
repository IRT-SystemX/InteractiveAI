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
  --color-card: var(--color-primary);
  background: var(--color-card);
  border-radius: var(--radius-medium);
  display: flex;
  cursor: pointer;

  &.primary {
    --color-card: var(--color-primary);
  }
  &.secondary {
    --color-card: var(--color-secondary);
  }
  &.success {
    --color-card: var(--color-success);
  }
  &.warning {
    --color-card: var(--color-warning);
  }
  &.error {
    --color-card: var(--color-error);
  }
  &.customColor {
    --color-card: v-bind(props.customColor);
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
    border-radius: var(--radius-medium);
    border: calc(var(--unit) / 4) solid var(--color-card);
    background-color: var(--color-grey-100);
    height: auto;
    flex: 1;
    transition: var(--duration);
    &:hover {
      background: var(--color-grey-200);
    }

    &:active {
      background: var(--color-grey-300);
    }
  }
}
</style>
