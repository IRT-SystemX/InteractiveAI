import axios from 'axios'

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
  function (error) {
    eventBus.emit('progress:stop')
    if (!['ERR_CANCELED'].includes(error.code))
      eventBus.emit('modal:open', {
        id: crypto.randomUUID(),
        data: t(`modal.error.${error.code}`) ?? error.message ?? error,
        type: 'info'
      })
    return Promise.reject(error)
  }
)
export default http
