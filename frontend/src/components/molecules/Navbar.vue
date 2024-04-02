<template>
  <nav>
    <div class="cab-nav">
      <RouterLink id="logo" :to="authStore.entities.length > 1 ? { name: 'home' } : ''">
        <SVG src="logo" :fill="modeColor()" :width="60"></SVG>
        <h1>
          {{ $t('cab') }}
          <div class="logo-infos" :title="JSON.stringify(env)">
            v{{ pkg.version }}
            <i
              v-if="env.MODE !== 'production'"
              :style="{
                'background-image': `linear-gradient(calc(var(--rotation) * 1deg), ${modeColor()} 50%, #fff)`
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
      <User />
      {{ authStore.user.userData.login }}
      <Button icon @click="logout"><LogIn /></Button>
    </div>
  </nav>
</template>
<script setup lang="ts">
import { LogIn, User } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { asset } from '@/utils/utils'

import pkg from '../../../package.json'
import Button from '../atoms/Button.vue'
import SVG from '../atoms/SVG.vue'

const env = import.meta.env

const authStore = useAuthStore()
const router = useRouter()

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
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 0 10px var(--color-grey-600);
  height: 100%;
  padding: var(--spacing-1);
  position: sticky;
  top: 0;
  width: 100vw;
  overflow: auto hidden;
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
        display: flex;
        flex-direction: column;
        font-size: 1rem;
        .mode {
          --rotation: 0;
          background-clip: text;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: spin 10s infinite linear;
        }
      }
    }
  }

  .cab-nav {
    height: 100%;
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
  }
}

@keyframes spin {
  to {
    --rotation: 360;
  }
}
</style>
