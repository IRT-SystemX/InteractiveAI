import axios, { AxiosError } from 'axios'

import router from '@/router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

import eventBus from './eventBus'
import i18n from './i18n'

const { t } = i18n.global

const http = axios.create({
  baseURL: import.meta.env.VITE_API,
  headers: { Accept: 'application/json' }
})

http.interceptors.request.use(
  function (config) {
    useAppStore().status.loading.push({ state: 'LOADING', data: config })
    // Add access token to all requests
    const authStore = useAuthStore()
    config.headers.Authorization = `Bearer ${authStore.token?.access_token}`
    return config
  },
  function (error) {
    useAppStore().status.loading[useAppStore().status.loading.findIndex((el) => el.data.url)] = {
      state: 'ERROR',
      data: error
    }
    return Promise.reject(error)
  }
)

http.interceptors.response.use(
  function (response) {
    useAppStore().status.loading.splice(
      useAppStore().status.loading.findIndex((el) => el.data.url),
      1
    )
    return response
  },
  async function (error: AxiosError<any, any>) {
    const authStore = useAuthStore()
    // If request failed, check if token is expired
    if (error.config?.url !== '/auth/check_token' && authStore.token?.access_token) {
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
    useAppStore().status.loading[useAppStore().status.loading.findIndex((el) => el.data.url)] = {
      state: 'ERROR',
      data: error
    }
    if (error.code && !['ERR_CANCELED'].includes(error.code))
      eventBus.emit('modal:open', {
        data:
          t('modal.error.default', {
            url: error.config?.url,
            code: error.code,
            message:
              error.response?.data?.error_description ??
              error.response?.data?.message ??
              error.response?.data?.error ??
              error.message
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
