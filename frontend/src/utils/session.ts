import i18n from '@/plugins/i18n'
import router from '@/router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

const { t } = i18n.global

/**
 * Reads the `exp` claim of a JWT without verifying its signature.
 * @param accessToken raw JWT
 * @returns expiry timestamp in ms, or `undefined` if the token is unreadable
 */
export function jwtExpiry(accessToken: string) {
  try {
    const payload = accessToken.split('.')[1]
    if (!payload) return undefined
    // base64url -> base64, re-adding the padding JWTs strip
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const json = JSON.parse(
      decodeURIComponent(
        atob(base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '='))
          .split('')
          .map((char) => '%' + char.charCodeAt(0).toString(16).padStart(2, '0'))
          .join('')
      )
    )
    return typeof json.exp === 'number' ? json.exp * 1000 : undefined
  } catch (err) {
    return undefined
  }
}

/**
 * Guard so the burst of 401s triggered by a stale token (context polling, card
 * subscription, current user, ...) only ever produces one modal and one redirect.
 */
let handling = false

/**
 * Single entry point for "this session is no longer usable".
 * Silences every pending/queued request error, logs the user out and asks them
 * to log in again instead of surfacing raw 401 payloads.
 *
 * @param options `redirect: false` when called from a navigation guard, which
 *   returns its own redirect and must not be raced by a `router.push`
 */
export function handleSessionExpired(options: { redirect?: boolean } = {}) {
  if (handling) return
  handling = true

  const appStore = useAppStore()
  const authStore = useAuthStore()

  // Drop the error modals/requests already queued by the 401 burst
  appStore._modals = []
  appStore.status.requests = []

  // `force: false` -> only export traces if the session actually recorded some,
  // so a stale token does not trigger a surprise file download on page load.
  // Leaving the CAB route unsubscribes from the card stream (CAB.vue
  // `onBeforeRouteLeave`), so nothing else needs tearing down here.
  authStore.logout('json', { force: false })

  appStore.addModal({
    data: t('modal.error.SESSION_EXPIRED'),
    type: 'info',
    callback: () => {
      handling = false
    }
  })

  if ((options.redirect ?? true) && router.currentRoute.value.name !== 'login')
    router.push({ name: 'login' })
}

/**
 * True while a session expiry is being handled, so error handlers further down
 * the promise chain can stay quiet instead of stacking their own modals.
 */
export function isHandlingSessionExpiry() {
  return handling
}

/** Called after a successful login so a later expiry is handled again. */
export function resetSessionExpiredGuard() {
  handling = false
}
