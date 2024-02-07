<template>
  <h1>{{ $t('cab.assistant') }}</h1>
  <main class="flex flex-1 flex-col">
    <slot>
      <div class="flex flex-1 flex-col color-primary flex-center">
        <SVG src="logo" fill="var(--color-primary)" :width="56" class="mb-3"></SVG>
        <h1 class="mb-1">{{ $t('assistant.cab.hello') }}</h1>
        <p class="text-center">{{ $t('assistant.cab.presentation') }}</p>
      </div>
    </slot>
  </main>
  <footer class="flex flex-center-y cab-chat">
    <div class="cab-chat-input">
      <input class="cab-input" :placeholder="$t('assistant.placeholder')" />
      <Mic color="var(--color-grey-600)" :height="24" />
    </div>
    <SVG src="logo" fill="var(--color-primary)" :width="32" class="ml-1"></SVG>
  </footer>
</template>
<script setup lang="ts">
import { Mic } from 'lucide-vue-next'

import SVG from '@/components/atoms/SVG.vue'
</script>
<style lang="scss">
.cab-assistant {
  gap: var(--spacing-1);
  main {
    display: flex;
    flex-direction: column;
    flex: 1;
    gap: var(--spacing-2);
    overflow: hidden auto;
    scrollbar-gutter: stable both-edges;
  }
}
.cab-chat {
  justify-content: space-between;

  &-input {
    flex: 1;
    position: relative;
    .cab-input {
      width: 100%;
    }

    svg {
      position: absolute;
      right: var(--spacing-1);
      top: 50%;
      transform: translateY(-50%);
      background: var(--color-grey-200);
    }
  }
}
</style>
