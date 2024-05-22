<template>
  <div
    ref="slot"
    class="cab-tooltip-slot"
    :class="[placement, toggle, { visible }]"
    @click="visible = !visible">
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
import {
  arrow,
  autoUpdate,
  flip,
  offset,
  type Placement,
  shift,
  useFloating
} from '@floating-ui/vue'
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    placement?: Placement
    textAlign?: 'center' | 'left' | 'right' | 'justified'
    toggle?: 'hover' | 'click'
  }>(),
  { placement: 'top', textAlign: 'center', toggle: 'hover' }
)

const visible = ref(false)
const slot = ref<HTMLElement | null>(null)
const tooltip = ref<HTMLDivElement | null>(null)
const floatingArrow = ref<HTMLDivElement | null>(null)

const { floatingStyles, middlewareData } = useFloating(slot, tooltip, {
  placement: props.placement,
  middleware: [flip(), shift(), arrow({ element: floatingArrow }), offset(8)],
  whileElementsMounted: autoUpdate
})
</script>
<style lang="scss">
.cab-tooltip {
  &-slot {
    display: inline-flex;
    width: min-content;
    cursor: pointer;
    &.hover:hover > .cab-tooltip-content,
    &.click.visible > .cab-tooltip-content,
    &.click:focus > .cab-tooltip-content {
      visibility: visible;
      opacity: 1;
    }

    &[class*='top'] .cab-tooltip-arrow {
      bottom: calc(var(--unit) / -2);
    }
    &[class*='bottom'] .cab-tooltip-arrow {
      top: calc(var(--unit) / -2);
    }
    &[class*='left'] .cab-tooltip-arrow {
      right: calc(var(--unit) / -2);
    }
    &[class*='right'] .cab-tooltip-arrow {
      left: calc(var(--unit) / -2);
    }
  }
  &-content {
    visibility: hidden;
    width: max-content;
    background-color: var(--color-grey-800);
    color: var(--color-text-inverted);
    text-align: v-bind('props.textAlign');
    padding: var(--spacing-1);
    border-radius: var(--radius-medium);
    z-index: 3000;
    max-width: 300px;
    opacity: 0;
    transition: opacity var(--duration);
  }
  &-arrow {
    width: var(--unit);
    height: var(--unit);
    transform: rotate(45deg);
    background: var(--color-grey-800);
  }
}
</style>
