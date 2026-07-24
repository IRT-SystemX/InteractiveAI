<template>
  <form @submit.prevent="login">
    <Avatar :size="300" />
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
import { useI18n } from 'vue-i18n'

import Avatar from '@/components/atoms/Avatar.vue'
import Button from '@/components/atoms/Button.vue'
import router from '@/router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { setCognitiveConsent } from '@/utils/consent'

const authStore = useAuthStore()
const appStore = useAppStore()
const { t } = useI18n()

const username = ref('')
const password = ref('')

async function login() {
  await authStore.login(username.value, password.value)
  // Ask the operator whether cognitive/stress data may be collected. Default to
  // "no consent" until they explicitly accept, so nothing is collected in the
  // gap before they answer.
  setCognitiveConsent(false)
  appStore.addModal({
    data: t('modal.consent.cognitive'),
    type: 'choice',
    callback: (success: boolean) => setCognitiveConsent(success)
  })
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
