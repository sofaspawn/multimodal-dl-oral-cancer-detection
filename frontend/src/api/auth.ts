/**
 * Authentication endpoints.
 *
 * None of these exist on the backend yet -- POST /register, POST /login and
 * GET /me are listed as planned in BACKEND_API.md. In mock mode any non-empty
 * credentials succeed.
 */

import { clearToken, getJson, postJson, setToken, USE_MOCKS } from './client'
import * as mocks from './mocks'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from './types'

export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = USE_MOCKS
    ? await mocks.login(credentials)
    : await postJson<AuthResponse>('/login', credentials)

  setToken(response.access_token)
  return response
}

export async function register(
  payload: RegisterRequest,
): Promise<AuthResponse> {
  const response = USE_MOCKS
    ? await mocks.register(payload)
    : await postJson<AuthResponse>('/register', payload)

  setToken(response.access_token)
  return response
}

export function me(): Promise<User> {
  if (USE_MOCKS) return mocks.me()
  return getJson<User>('/me')
}

export function logout(): void {
  clearToken()
}
