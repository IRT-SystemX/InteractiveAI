<template>
  <div ref="slot" class="cab-tooltip-slot">
    <slot />
    <div ref="tooltip" class="cab-tooltip-content" :style="floatingStyles">
      <slot name="tooltip"></slot>
      <div
        ref="floatingArrow"
        class="cab-tooltip-arrow"
        :style="{
          position: 'absolute',
          left: middlewareData.arrow?.x != null ? `${middlewareData.arrow.x}px` : '',
          top: middlewareData.arrow?.y != null ? `${middlewareData.arrow.y}px` : ''
        }"></div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { arrow, autoUpdate, flip, offset, shift, useFloating } from '@floating-ui/vue'
import { ref } from 'vue'

const slot = ref<HTMLElement | null>(null)
const tooltip = ref<HTMLDivElement | null>(null)
const floatingArrow = ref<HTMLDivElement | null>(null)

const { floatingStyles, middlewareData } = useFloating(slot, tooltip, {
  placement: 'top',
  middleware: [offset(8), flip(), shift(), arrow({ element: floatingArrow, padding: 8 })],
  whileElementsMounted: autoUpdate
})
</script>
<style lang="scss">
.cab-tooltip {
  &-slot:hover .cab-tooltip-content {
    pointer-events: none;
    opacity: 1;
  }
  &-content {
    transition: var(--duration);
    opacity: 0;
    width: max-content;
    display: block;
    background-color: var(--color-grey-800);
    color: var(--color-text-inverted);
    text-align: center;
    padding: var(--spacing-1);
    border-radius: var(--radius-medium);
    z-index: 3000;
  }
  &-arrow {
    margin-top: calc(var(--unit) / 2);
    width: var(--unit);
    height: var(--unit);
    transform: rotate(45deg);
    background: var(--color-grey-800);
  }
}
</style>
