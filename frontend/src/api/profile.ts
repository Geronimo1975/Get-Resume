import api from './client'
import type { UserProfile } from '@/types'

export function fetchProfile() {
  return api.get<UserProfile>('/users/me/profile/')
}

export function updateProfile(payload: Partial<UserProfile>) {
  return api.patch<UserProfile>('/users/me/profile/', payload)
}

export function requestGdprExport() {
  return api.post('/users/me/gdpr-export/')
}

export function requestGdprDeletion() {
  return api.post('/users/me/gdpr-delete/')
}
