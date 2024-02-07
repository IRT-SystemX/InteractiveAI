<template>
  <form @submit.prevent="login">
    <input
      v-model="username"
      type="text"
      autofocus
      autocomplete="username"
      class="cab-input mb-2"
      :placeholder="$t('input.placeholder.username')" />
    <input
      v-model="password"
      autocomplete="current-password"
      type="password"
      class="cab-input mb-2"
      :placeholder="$t('input.placeholder.password')" />
    <Button type="submit">{{ $t('button.login') }}</Button>
  </form>
</template>
<script setup lang="ts">
import { ref } from 'vue'

import Button from '@/components/atoms/Button.vue'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const username = ref('')
const password = ref('')

async function login() {
  await authStore.login(username.value, password.value)
  router.push('/')
}
</script>
<style scoped>
form {
  display: flex;
  height: 100%;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
