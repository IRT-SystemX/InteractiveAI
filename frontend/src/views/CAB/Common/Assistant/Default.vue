<template>
  <h1>{{ $t('cab.assistant') }}</h1>
  <slot name="default">
    <main class="flex flex-1 flex-center flex-col color-primary">
      <SVG src="logo" fill="var(--color-primary)" :width="56" class="mb-3"></SVG>
      <h1 class="mb-1">{{ $t('assistant.cab.hello') }}</h1>
      <p class="text-center">{{ $t('assistant.cab.presentation') }}</p>
    </main>
  </slot>
  <footer class="flex flex-center-v cab-chat">
    <div class="cab-chat-input">
      <input class="cab-input" :placeholder="$t('assistant.placeholder')" />
      <Mic color="var(--color-grey-600)" :height="24" />
    </div>
    <SVG src="logo" fill="var(--color-primary)" :width="32"></SVG>
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
    flex: 1;
    gap: var(--spacing-2);
    overflow: hidden auto;
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
    }
  }
}
</style>
