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

export function refreshToken(refresh_token: string, client_id: string, client_secret: string) {
  return http.post(
    '/auth/token',
    new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token,
      client_id,
      client_secret
    })
  )
}

export function checkToken() {
  return http.post('/auth/check_token')
}

export function synchronizeWithToken() {
  return http.post('/users/users/synchronizeWithToken')
}

export function getCurrentUser() {
  return http.get<UserResponse>('/users/CurrentUserWithPerimeters')
}
