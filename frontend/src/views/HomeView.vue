<template>
  <div v-if="authStore.entities.length" class="deck p-6">
    <RouterLink
      v-for="entity of authStore.entities"
      :key="entity"
      :to="{ name: 'cab', params: { entity } }">
      <Card>
        <template #outer>
          <img :src="asset(`img/entities/${entity}.svg`)" />
        </template>
        {{ $t(`entity.${entity}`) }}
      </Card>
    </RouterLink>
  </div>
  <div v-else class="flex flex-center h-100">Aucune entité</div>
</template>
<script setup lang="ts">
import { RouterLink } from 'vue-router'

import Card from '@/components/atoms/Card.vue'
import { useAuthStore } from '@/stores/auth'
import { asset } from '@/utils/utils'

const authStore = useAuthStore()
</script>
<style lang="scss">
.deck {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-6);
  height: 100%;

  a {
    flex: 1;
    height: fit-content;

    .cab-card {
      aspect-ratio: 16/9;
      max-height: calc(var(--unit) * 20);
      width: 100%;

      &-outer {
        width: 33%;
        img {
          max-width: 100%;
          max-height: 100%;
          filter: brightness(0.5) grayscale(1) contrast(3) invert(1);
        }
      }

      &-inner {
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
  }
}
</style>
