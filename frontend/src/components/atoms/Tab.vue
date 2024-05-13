<template>
  <button class="cab-tab" :class="{ active }"><slot></slot></button>
</template>
<script setup lang="ts">
defineProps<{
  active?: boolean
}>()
</script>
<style lang="scss">
.cab-tab-container {
  padding: 0 calc(var(--unit) / 2);
  border-bottom: 1px solid var(--color-grey-300);
}
.cab-tab {
  cursor: pointer;
  background: linear-gradient(
    145deg,
    color-mix(in srgb, var(--color-grey-200), #fff 15%),
    color-mix(in srgb, var(--color-grey-200), #fff 15%)
  );
  font-family: 'Lexend';
  font-weight: 700;
  border: none;
  box-shadow:
    calc(var(--unit) * 0.25) calc(var(--unit) * 0.25) calc(var(--unit) * 0.5)
      color-mix(in srgb, var(--color-grey-200), #000 15%),
    calc(var(--unit) * -0.25) calc(var(--unit) * -0.25) calc(var(--unit) * 0.5)
      color-mix(in srgb, var(--color-grey-200), #fff 15%);
  border-radius: var(--radius-small) var(--radius-small) 0 0;
  margin: 0 var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);

  &.active {
    position: relative;
    color: var(--color-primary);
    box-shadow:
      inset calc(var(--unit) * 0.5) calc(var(--unit) * 0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--color-grey-200), #000 15%),
      inset calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
        color-mix(in srgb, var(--color-grey-200), #fff 15%);
    background: var(--color-background);
    border-color: var(--color-grey-300);
  }
}
</style>
