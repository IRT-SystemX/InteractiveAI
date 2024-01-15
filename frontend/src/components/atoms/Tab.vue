<template>
  <button class="cab-tab" :class="{ active }"><slot name="default"></slot></button>
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
  background: var(--color-grey-200);
  border: 1px solid var(--color-grey-300);
  border-bottom: none;
  border-radius: var(--radius-small) var(--radius-small) 0 0;
  margin: 0 var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);

  &.active {
    position: relative;
    background: var(--color-background);
    border-color: var(--color-grey-300);
  }
}
</style>
