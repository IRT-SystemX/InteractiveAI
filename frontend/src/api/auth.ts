import http from '@/plugins/http'
import type { LoginResponse, UserResponse } from '@/types/auth'

export function login(username: string, password: string) {
  return http.post<LoginResponse>(
    '/auth/token',
    // Why isn't it just a json?
    new URLSearchParams({
      username,
      password,
      grant_type: 'password',
      clientId: 'opfab-client'
    })
  )
}

/**
 * Exchanges the refresh token for a fresh access token. Client credentials are
 * injected by the nginx proxy as a Basic auth header (same as `login`), so only
 * the grant and the refresh token travel in the body.
 */
export function refreshToken(refresh_token: string) {
  return http.post<LoginResponse>(
    '/auth/token',
    new URLSearchParams({
      refresh_token,
      grant_type: 'refresh_token',
      clientId: 'opfab-client'
    }),
    // A dead refresh token is expected: the caller turns it into a session
    // expiry, so it must not raise a generic error popup of its own.
    { _silent: true }
  )
}

export function checkToken(token: string) {
  return http.post<{ active: boolean }>(
    '/auth/check_token',
    new URLSearchParams({
      token
    })
  )
}

// TODO
export function synchronizeWithToken() {
  return http.post('/users/users/synchronizeWithToken')
}

export function getCurrentUser() {
  return http.get<UserResponse>('/users/CurrentUserWithPerimeters')
}
