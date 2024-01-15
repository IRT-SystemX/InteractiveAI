import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as auth from '@/api/auth'
import type { LoginResponse, UserResponse } from '@/types/auth'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref<LoginResponse>()
    const user = ref<UserResponse>()
    const entities = computed(() =>
      user.value
        ? user.value.userData.entities
            .filter((entity) => ['DA', 'ORANGE', 'RTE', 'SNCF'].includes(entity))
            .sort()
        : []
    )

    async function login(username: string, password: string) {
      const tokenRes = await auth.login(username, password)
      token.value = tokenRes.data
      const userRes = await auth.getCurrentUser()
      user.value = userRes.data
    }

    function logout() {
      token.value = undefined
      user.value = undefined
    }

    return { token, user, entities, login, logout }
  },
  { persist: true }
)
