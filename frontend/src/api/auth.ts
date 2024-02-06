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

// TODO: typing
export function checkToken(token: string) {
  return http.post(
    '/auth/check_token',
    new URLSearchParams({
      token
    })
  )
}

// TODO: typing
export function synchronizeWithToken() {
  return http.post('/users/users/synchronizeWithToken')
}

// TODO: typing
export function getCurrentUser() {
  return http.get<UserResponse>('/users/CurrentUserWithPerimeters')
}
