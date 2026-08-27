import axios, { AxiosError } from 'axios'

import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { handleSessionExpired, isHandlingSessionExpiry } from '@/utils/session'

import i18n from './i18n'

const { t } = i18n.global

declare module 'axios' {
  export interface AxiosRequestConfig {
    /** Internal: this request was already replayed after a token refresh. */
    _retried?: boolean
    /** Suppress the generic error modal - the caller handles failures itself. */
    _silent?: boolean
  }
}

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

    // The access token is short-lived (5 min on the demo realm). A 401 usually
    // just means it aged out mid-scenario, so renew it and replay the request
    // once. Only when the refresh token is gone too is the session really over,
    // and then we collapse the whole 401 burst into a single "log in again"
    // modal rather than one raw error popup per failed request.
    const isAuthRequest = ['/auth/token', '/auth/check_token'].includes(error.config?.url ?? '')
    if (error.response?.status === 401 && !isAuthRequest) {
      const config = error.config
      if (config && !config._retried && authStore.canRefresh) {
        config._retried = true
        if (await authStore.refresh()) {
          // Drop this attempt's LOADING entry; the replay pushes its own
          appStore.status.requests.splice(
            appStore.status.requests.findIndex((el) => el.data.url),
            1
          )
          return http(config)
        }
      }
      // Session is unrecoverable. Announce it once; stay silent afterwards
      // (token already cleared) so trailing 401s produce no popups at all.
      if (authStore.token?.access_token) handleSessionExpired()
      return Promise.reject(error)
    }
    // Trailing failures of requests started before the expiry was detected, and
    // calls that handle their own errors (the refresh grant), raise no popup.
    if (isHandlingSessionExpiry() || error.config?._silent) {
      appStore.status.requests.splice(
        appStore.status.requests.findIndex((el) => el.data.url),
        1
      )
      return Promise.reject(error)
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
