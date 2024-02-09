export type LoginResponse = {
  access_token: string
  expires_in: number
  refresh_expires_in: number
  refresh_token: string
  token_type: string
  'not-before-policy': number
  session_state: string
  scope: string
}

export type UserResponse = {
  userData: {
    login: string
    firstName: null | string
    lastName: null | string
    entities: string[]
    authorizedIPAddresses: string[]
    groups: string[]
  }
  computedPerimeters: string[]
  processesStatesNotNotified: any
}
