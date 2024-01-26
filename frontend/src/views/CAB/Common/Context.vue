<template>
  <main class="flex flex-col">
    <aside class="cab-context-tabs">
      <Tab
        v-for="(tab, index) of tabs"
        :key="tab"
        :active="modelValue === index"
        @click="$emit('update:modelValue', index)">
        {{ tab }}
      </Tab>
    </aside>
    <section class="cab-panel flex-center p-0 flex-1">
      <slot></slot>
    </section>
  </main>
</template>
<script setup lang="ts">
import Tab from '@/components/atoms/Tab.vue'

defineProps<{ tabs: string[]; modelValue: number }>()

defineEmits(['update:modelValue'])
</script>
<style lang="scss">
.cab-context {
  display: flex;
  flex-direction: column;
  .cab-context-tabs {
    display: flex;
    margin: 0 var(--spacing-2);
    overflow: auto;
    z-index: 1;
    transform: rotateX(180deg);
    .cab-tab {
      transform: rotateX(180deg);
    }
  }
  section {
    overflow: auto;
    position: relative;
    flex: 1;
    > * {
      position: absolute;
    }
  }
}
</style>
