import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as auth from '@/api/auth'
import type { LoginResponse, UserResponse } from '@/types/auth'
import { ENTITIES, type Entity } from '@/types/entities'
import { clearCognitiveConsent } from '@/utils/consent'
import { jwtExpiry, resetSessionExpiredGuard } from '@/utils/session'
import { clearTraceSession, exportTraceSession, startTraceSession } from '@/utils/traceSessionExport'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref<LoginResponse>()
    const user = ref<UserResponse>()
    const expireDate = ref<number>()
    const refreshExpireDate = ref<number>()

    /** Refresh this long before the access token actually dies. */
    const REFRESH_MARGIN_MS = 60_000
    /** Never schedule a refresh closer than this, to avoid a hot loop. */
    const MIN_REFRESH_DELAY_MS = 5_000

    let refreshTimer: number | undefined
    /** In-flight refresh, shared so a burst of 401s triggers only one call. */
    let refreshing: Promise<boolean> | undefined
    const entities = computed(() =>
      user.value
        ? user.value.userData.entities
            .filter((entity) => ENTITIES.includes(entity as Entity))
            .sort()
        : []
    )

    /**
     * True when the persisted token is known to be expired. The `exp` claim is
     * authoritative (it survives a reload); `expireDate` is only a fallback for
     * tokens we cannot decode. When neither is readable we stay optimistic and
     * let the API answer.
     */
    const isTokenExpired = computed(() => {
      if (!token.value?.access_token) return true
      const expiry = jwtExpiry(token.value.access_token) ?? expireDate.value
      return expiry ? Date.now() >= expiry : false
    })

    /** True while the refresh token itself is still usable. */
    const canRefresh = computed(
      () =>
        !!token.value?.refresh_token &&
        (!refreshExpireDate.value || Date.now() < refreshExpireDate.value)
    )

    function applyToken(data: LoginResponse) {
      token.value = data
      expireDate.value = Date.now() + data.expires_in * 1000
      refreshExpireDate.value = data.refresh_expires_in
        ? Date.now() + data.refresh_expires_in * 1000
        : undefined
    }

    /**
     * Arms a timer that renews the access token shortly before it expires, so a
     * long scenario never hits a 401 in the first place. Re-armed after every
     * successful refresh; cleared on logout.
     */
    function scheduleRefresh() {
      stopRefresh()
      if (!canRefresh.value || !expireDate.value) return
      const delay = Math.max(
        expireDate.value - Date.now() - REFRESH_MARGIN_MS,
        MIN_REFRESH_DELAY_MS
      )
      refreshTimer = window.setTimeout(() => void refresh(), delay)
    }

    function stopRefresh() {
      if (refreshTimer !== undefined) window.clearTimeout(refreshTimer)
      refreshTimer = undefined
    }

    /**
     * Renews the access token. Concurrent callers share one request, so a burst
     * of 401s cannot stampede Keycloak.
     * @returns whether a usable token is now in place
     */
    function refresh(): Promise<boolean> {
      if (refreshing) return refreshing
      if (!canRefresh.value) return Promise.resolve(false)
      refreshing = auth
        .refreshToken(token.value!.refresh_token)
        .then(({ data }) => {
          applyToken(data)
          resetSessionExpiredGuard()
          scheduleRefresh()
          return true
        })
        .catch(() => {
          stopRefresh()
          return false
        })
        .finally(() => {
          refreshing = undefined
        })
      return refreshing
    }

    async function login(username: string, password: string) {
      const tokenRes = await auth.login(username, password)
      applyToken(tokenRes.data)
      resetSessionExpiredGuard()
      scheduleRefresh()
      const userRes = await auth.getCurrentUser()
      user.value = userRes.data
      try {
        startTraceSession(userRes.data.userData.login)
      } catch (error) {
        console.warn('Unable to start trace session export:', error)
      }
    }

    async function checkToken() {
      const { data } = await auth.checkToken(token.value?.access_token!)
      return data.active
    }

    /**
     * @param format trace export format
     * @param options `force: false` skips the export when the session recorded
     *   no trace - used on session expiry so no empty file is downloaded
     */
    function logout(format: 'json' | 'csv' = 'json', options: { force?: boolean } = {}) {
      try {
        exportTraceSession(format, {
          force: options.force ?? true,
          userLogin: user.value?.userData.login
        })
      } catch (error) {
        console.warn('Unable to export trace session:', error)
      } finally {
        stopRefresh()
        clearTraceSession()
        clearCognitiveConsent()
        token.value = undefined
        user.value = undefined
        expireDate.value = undefined
        refreshExpireDate.value = undefined
        localStorage.removeItem('context')
      }
    }

    return {
      token,
      user,
      expireDate,
      refreshExpireDate,
      entities,
      isTokenExpired,
      canRefresh,
      login,
      logout,
      checkToken,
      refresh,
      scheduleRefresh
    }
  },
  { persist: true }
)
