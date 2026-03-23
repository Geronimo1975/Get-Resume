import api from './client'
import type { User, AuthTokens } from '@/types'

export function loginApi(email: string, password: string) {
  return api.post<AuthTokens & { user: User }>('/auth/login/', { email, password })
}

export function registerApi(payload: {
  email: string
  password1: string
  password2: string
  first_name: string
  last_name: string
}) {
  return api.post<AuthTokens & { user: User }>('/auth/registration/', payload)
}

export function logoutApi() {
  return api.post('/auth/logout/')
}

export function refreshApi(refresh: string) {
  return api.post<{ access: string; refresh?: string }>('/auth/token/refresh/', { refresh })
}

export function fetchUserApi() {
  return api.get<User>('/users/me/')
}

export function resendVerificationApi(email: string) {
  return api.post('/auth/registration/resend-email/', { email })
}

export function verifyEmailApi(key: string) {
  return api.post('/auth/registration/verify-email/', { key })
}

export function resetPasswordApi(email: string) {
  return api.post('/auth/password/reset/', { email })
}

export function resetPasswordConfirmApi(payload: {
  uid: string
  token: string
  new_password1: string
  new_password2: string
}) {
  return api.post('/auth/password/reset/confirm/', payload)
}
