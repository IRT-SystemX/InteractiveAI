import axios, { AxiosError } from 'axios'

import router from '@/router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

import i18n from './i18n'

const { t } = i18n.global

const http = axios.create({
  baseURL: import.meta.env.VITE_API,
  headers: { Accept: 'application/json' }
})

http.interceptors.request.use(
  function (config) {
    useAppStore().status.requests.push({ state: 'LOADING', data: config })
    // Add access token to all requests
    const authStore = useAuthStore()
    config.headers.Authorization = `Bearer ${authStore.token?.access_token}`
    return config
  },
  function (error) {
    const appStore = useAppStore()
    appStore.status.requests[appStore.status.requests.findIndex((el) => el.data.url)] = {
      state: 'ERROR',
      data: error
    }
    return Promise.reject(error)
  }
)

http.interceptors.response.use(
  function (response) {
    const appStore = useAppStore()
    appStore.status.requests.splice(
      appStore.status.requests.findIndex((el) => el.data.url),
      1
    )
    return response
  },
  async function (error: AxiosError<any, any>) {
    const authStore = useAuthStore()
    const appStore = useAppStore()
    // If request failed, check if token is expired
    if (error.config?.url !== '/auth/check_token' && authStore.token?.access_token) {
      const res = await authStore.checkToken()
      if (!res) {
        appStore._modals = []
        appStore.addModal({
          data: t('modal.error.DISCONNECTED'),
          type: 'info',
          callback: () => {
            appStore.status.requests = []
          }
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
    appStore.status.requests[appStore.status.requests.findIndex((el) => el.data.url)] = {
      state: 'ERROR',
      data: error
    }
    if (error.code && !['ERR_CANCELED'].includes(error.code))
      appStore.addModal({
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
        type: 'info',
        callback: () => {
          appStore.status.requests.splice(
            appStore.status.requests.findIndex((el) => el.data.url),
            1
          )
        }
      })
    return Promise.reject(error)
  }
)
export default http
