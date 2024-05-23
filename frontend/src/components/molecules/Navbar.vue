<template>
  <nav>
    <div class="cab-nav">
      <RouterLink id="logo" :to="authStore.entities.length > 1 ? { name: 'home' } : ''">
        <SVG src="/img/logo.svg" :fill="modeColor()" :height="32" class="ml-2 mr-1"></SVG>
        <h1 class="cab-logo-typo">
          {{ $t('cab') }}
          <div class="logo-infos" :title="JSON.stringify(env)">
            {{ pkg.version }}
            <i
              v-if="env.MODE !== 'production'"
              :style="{
                color: modeColor()
              }"
              class="mode">
              {{ env.MODE }}
            </i>
          </div>
        </h1>
      </RouterLink>
      <template v-if="authStore.entities.length > 1">
        <RouterLink
          v-for="entity of authStore.entities"
          :key="entity"
          class="flex flex-center-y entity"
          :to="{ name: 'cab', params: { entity } }">
          <img :src="asset(`entities/${entity}/assets/logo.svg`)" width="32" height="32" />
        </RouterLink>
      </template>
    </div>
    <div v-if="authStore.user" class="cab-nav">
      <Tooltip placement="bottom">
        <template #tooltip>
          {{ $t('cab.status.requests') }} {{ $t(`cab.status.${appStore.requestsStatus}`) }}
        </template>
        <div
          :key="appStore.requestsStatus"
          class="flex flex-center-y cab-status"
          :class="[appStore.requestsStatus]">
          <ArrowUpDown :size="16"></ArrowUpDown>
        </div>
      </Tooltip>
      <TransitionGroup name="fade">
        <Tooltip v-if="authStore.user" placement="bottom">
          <template #tooltip>
            {{ $t('cab.status.notifications') }}
            {{ $t(`cab.status.${appStore.status.notifications.state}`) }}
          </template>
          <div
            :key="appStore.status.notifications.last"
            class="flex flex-center-y cab-status"
            :class="[appStore.status.notifications.state]"
            @click="cardsStore.subscribe($route.params.entity as Entity)">
            <Bell :size="16"></Bell>
          </div>
        </Tooltip>
        <Tooltip v-if="appStore.status.context.state !== 'NONE'" placement="bottom">
          <template #tooltip>
            {{ $t('cab.status.context') }} {{ $t(`cab.status.${appStore.status.context.state}`) }}
          </template>
          <div
            :key="appStore.status.context.last"
            class="flex flex-center-y cab-status"
            :class="[appStore.status.context.state]">
            <AppWindow :size="16"></AppWindow>
          </div>
        </Tooltip>
      </TransitionGroup>
      <User />
      {{ authStore.user.userData.login }}
      <Button icon :aria-label="$t('button.login')" @click="logout"><LogIn /></Button>
    </div>
  </nav>
</template>
<script setup lang="ts">
import { AppWindow, ArrowUpDown, Bell, LogIn, User } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useCardsStore } from '@/stores/cards'
import type { Entity } from '@/types/entities'
import { asset } from '@/utils/utils'

import pkg from '../../../package.json'
import Button from '../atoms/Button.vue'
import SVG from '../atoms/SVG.vue'
import Tooltip from '../atoms/Tooltip.vue'

const env = import.meta.env

const router = useRouter()
const authStore = useAuthStore()
const cardsStore = useCardsStore()
const appStore = useAppStore()

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}

function modeColor() {
  switch (env.MODE) {
    case 'development':
      return 'var(--color-success)'
    case 'simu':
      return 'var(--color-warning)'
    case 'prod':
      return 'var(--color-error)'
    case 'demo':
      return 'var(--color-primary)'
    case 'production':
      return 'var(--color-primary)'
    default:
      return 'var(--color-primary)'
  }
}
</script>
<style scoped>
@property --rotation {
  syntax: '<number>';
  initial-value: 0;
  inherits: false;
}
</style>
<style scoped lang="scss">
html.dark nav .entity {
  filter: brightness(0.5) grayscale(1) contrast(3) invert(1);
}
nav {
  display: flex;
  overflow: auto;
  align-items: center;
  justify-content: space-between;
  box-shadow:
    inset calc(var(--unit) * 0.5) calc(var(--unit) * 0.5) calc(var(--unit) * 1)
      color-mix(in srgb, var(--color-background), #000 20%),
    inset calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
      color-mix(in srgb, var(--color-background), #ccc 20%);
  height: 100%;
  width: 100%;
  border-radius: var(--radius-circular);
  z-index: 1000;

  .entity {
    filter: grayscale(1);
    &:hover,
    &.router-link-exact-active {
      filter: none !important;
    }
  }

  #logo {
    display: flex;
    align-items: center;
    font-size: 2rem;
    font-weight: bold;
    color: var(--color-text);
    background: none;
    align-items: center;
    height: 100%;
    svg {
      height: 100%;
    }
    h1 {
      font-size: 2rem;
      display: flex;

      .logo-infos {
        font-family: Inter, sans-serif;
        display: flex;
        flex-direction: column;
        font-size: 0.8rem;
        font-weight: 900;
        justify-content: center;
      }
    }
  }

  .cab-nav {
    height: 100%;
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
  }
  .cab-status {
    --color-cab-status: var(--color-text);
    background-color: var(--color-cab-status);
    margin: auto;
    padding: var(--spacing-1);
    color: var(--color-text-inverted);
    border-radius: var(--radius-circular);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.8;
    transition: opacity var(--duration);
    .lucide {
      filter: drop-shadow(
          calc(var(--unit) * 0.5) calc(var(--unit) * 0.5) calc(var(--unit) * 1)
            color-mix(in srgb, var(--color-cab-status), #000 20%)
        )
        drop-shadow(
          calc(var(--unit) * -0.5) calc(var(--unit) * -0.5) calc(var(--unit) * 1)
            color-mix(in srgb, var(--color-cab-status), #ccc 20%)
        );
    }
    &:hover {
      opacity: 1;
    }

    &.OFFLINE,
    &.ERROR {
      --color-cab-status: var(--color-error);
    }
    &.FROZEN {
      --color-cab-status: var(--color-warning);
      animation: ripple 1s alternate infinite;
    }
    &.ONLINE,
    &.IDLE,
    &.LOADING {
      --color-cab-status: var(--color-primary);
      animation: ripple 1s;
    }
    &.LOADING {
      animation: ripple 1s alternate infinite;
    }
  }
}

@keyframes ripple {
  0% {
    box-shadow: 0 0 0 0rem var(--color-cab-status);
  }
  100% {
    box-shadow: 0 0 0 1rem transparent;
  }
}

@keyframes spin {
  to {
    --rotation: 360;
  }
}
</style>
