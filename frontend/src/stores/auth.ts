import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as auth from '@/api/auth'
import type { LoginResponse, UserResponse } from '@/types/auth'
import { ENTITIES, type Entity } from '@/types/entities'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref<LoginResponse>()
    const user = ref<UserResponse>()
    const expireDate = ref<number>()
    const entities = computed(() =>
      user.value
        ? user.value.userData.entities
            .filter((entity) => ENTITIES.includes(entity as Entity))
            .sort()
        : []
    )

    async function login(username: string, password: string) {
      const tokenRes = await auth.login(username, password)
      token.value = tokenRes.data
      expireDate.value = Date.now() + tokenRes.data.expires_in * 1000
      const userRes = await auth.getCurrentUser()
      user.value = userRes.data
    }

    async function checkToken() {
      const { data } = await auth.checkToken(token.value?.access_token!)
      return data.active
    }

    function logout() {
      token.value = undefined
      user.value = undefined
      localStorage.removeItem('context')
    }

    return { token, user, entities, login, logout, checkToken }
  },
  { persist: true }
)
