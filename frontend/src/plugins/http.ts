import axios from 'axios'

import router from '@/router'
import { useAuthStore } from '@/stores/auth'

import eventBus from './eventBus'
import i18n from './i18n'

const { t } = i18n.global

const http = axios.create({
  baseURL: import.meta.env.VITE_API
})

http.interceptors.request.use(
  function (config) {
    eventBus.emit('progress:start')
    // Add access token to all requests
    const authStore = useAuthStore()
    config.headers.Authorization = `Bearer ${authStore.token?.access_token}`
    return config
  },
  function (error) {
    eventBus.emit('progress:stop')
    return Promise.reject(error)
  }
)

http.interceptors.response.use(
  function (response) {
    eventBus.emit('progress:stop')
    return response
  },
  async function (error) {
    const authStore = useAuthStore()
    // If request failed, check if token is expired
    if (error.config.url !== '/auth/check_token') {
      const res = await authStore.checkToken()
      if (!res) {
        eventBus.emit('modal:open', {
          data: t('modal.error.DISCONNECTED'),
          type: 'info'
        })
        authStore.logout()
        router.push({ name: 'login' })
        return
      }
    } else {
      // If the request that failed was the token check,
      // then it is probably a network error and simply log out the user
      authStore.logout()
      router.push({ name: 'login' })
    }
    eventBus.emit('progress:stop')
    if (!['ERR_CANCELED', 'ERR_BAD_REQUEST'].includes(error.code)) console.error(error)
    eventBus.emit('modal:open', {
      data:
        t('modal.error.default', {
          url: error.config.url,
          code: error.code,
          message: error.message
        }) ??
        error.message ??
        t(`modal.error.${error.code}`) ??
        error,
      type: 'info'
    })
    return Promise.reject(error)
  }
)
export default http
