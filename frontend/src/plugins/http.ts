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
    // Do something before request is sent
    const authStore = useAuthStore()
    config.headers.Authorization = `Bearer ${authStore.token?.access_token}`
    return config
  },
  function (error) {
    eventBus.emit('progress:stop')
    // Do something with request error
    return Promise.reject(error)
  }
)

http.interceptors.response.use(
  function (response) {
    eventBus.emit('progress:stop')
    return response
  },
  async function (error) {
    if (error.config.url !== '/auth/check_token') {
      const authStore = useAuthStore()
      const res = await authStore.checkToken()
      if (!res) {
        eventBus.emit('modal:open', {
          data: t('modal.error.DISCONNECTED'),
          type: 'info'
        })
        authStore.logout()
        router.push({ name: 'login' })
      }
      return
    }
    eventBus.emit('progress:stop')
    if (!['ERR_CANCELED', 'ERR_BAD_REQUEST'].includes(error.code))
      eventBus.emit('modal:open', {
        data: t(`modal.error.${error.code}`) ?? error.message ?? error,
        type: 'info'
      })
    return Promise.reject(error)
  }
)
export default http
