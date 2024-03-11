<template>
  <div id="cab-graph" ref="graphHTML"></div>
</template>
<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { useGraphStore } from '@/stores/components/graph'

const graphStore = useGraphStore()

const graphHTML = ref<HTMLDivElement>()

onMounted(() => {
  graphStore.setup(
    {
      nodes: Array.from(Array(28).keys()).map((i) => ({ id: i + 1, status: [], selected: false })),
      links: []
    },
    graphHTML.value!
  )
})

watch(
  () => graphStore.data,
  (value) => {
    graphStore.setup(value!, graphHTML.value!)
  }
)
</script>
<style lang="scss">
#cab-graph {
  --duration: 0.3s;
  --unit: 4px;
  --white-900: #fff;
  --white-800: #f6f6f6;
  --white-500: #999;
  --black-100: #000;
  --red-500: #f55;
  --blue-500: #4bb4e6;
  --orange-500: #ff7900;
  --green-500: #50be87;

  position: relative;
  height: 100%;
  width: 100%;
  overflow: hidden;
  * {
    user-select: none;
  }
  svg {
    height: 100%;
    width: 100%;
    cursor: move;
    overscroll-behavior: none;
    &:active {
      cursor: grabbing;
    }
  }

  .node *,
  .link {
    transition: var(--duration);
  }

  .node,
  .tooltip {
    transition: opacity var(--duration);
  }

  .node {
    cursor: grab;
    --node-text: var(--white-500);
    --node-fill: var(--white-900);
    --node-stroke: var(--white-500);
    --stroke-width: var(--unit);
    --font-size: 1.2em;
  }

  .node:active {
    cursor: grabbing;
  }

  .node text {
    text-anchor: middle;
    fill: var(--node-text);
    font-size: var(--font-size);
    font-weight: bold;
  }

  .node circle {
    fill: var(--node-fill);
    stroke: var(--node-stroke);
    stroke-width: var(--stroke-width);
    paint-order: stroke;
  }

  .node:hover {
    --node-text: var(--blue-500);
    --node-stroke: var(--blue-500);
  }

  .node.active {
    --node-stroke: var(--blue-500);
    --node-text: var(--blue-500);
  }

  .node.focus {
    --stroke-width: calc(var(--unit) * 2);
    --font-size: 1.6em;
    --node-fill: var(--white-800);
  }

  .node.INFORMATION {
    --node-stroke: var(--green-500);
    --node-text: var(--green-500);
  }

  .node.ACTION {
    --node-stroke: var(--color-error);
    --node-text: var(--color-error);
  }

  .node.ALARM {
    --node-stroke: var(--color-error);
    --node-text: var(--color-error);
  }

  .link {
    stroke-width: 12;
    stroke: var(--white-500);
    cursor: pointer;
  }

  .link:hover,
  .link.focus {
    stroke: var(--blue-500) !important;
  }

  .link.active {
    stroke: var(--color-grey-900);
  }
}
</style>
