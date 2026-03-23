import api from './client'
import type { PaginatedResponse } from '@/types'

// --- Types ---

export interface AdminStats {
  users: {
    total: number
    active_30d: number
    new_today: number
    premium: number
    free: number
  }
  documents: {
    total: number
    created_today: number
    created_7d: number
    by_type: { lebenslauf: number; anschreiben: number; deckblatt: number }
  }
  system: {
    uptime: string
    version: string
    db_size: string
    redis_memory: string
  }
  subscriptions: {
    free: number
    premium_monthly: number
    premium_yearly: number
    business: number
  }
  recent_signups: Array<{
    id: string
    email: string
    first_name: string
    last_name: string
    date_joined: string
  }>
  recent_documents: Array<{
    id: string
    title: string
    doc_type: string
    user_email: string
    created_at: string
  }>
}

export interface AdminUser {
  id: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_email_verified: boolean
  date_joined: string
  last_login: string | null
  subscription_plan: string
  document_count: number
  profile?: {
    anrede: string
    geburtsdatum: string | null
    telefon: string
    strasse: string
    plz: string
    stadt: string
    bundesland: string
    preferred_language: string
  }
}

export interface AdminDocument {
  id: string
  title: string
  doc_type: string
  user_email: string
  template_name: string | null
  is_premium: boolean
  created_at: string
  updated_at: string
  deleted_at: string | null
  section_count: number
}

// --- API Functions ---

export async function fetchAdminStats(): Promise<AdminStats> {
  const { data } = await api.get('/admin/stats/')
  return data
}

export async function fetchAdminUsers(params: {
  page?: number
  search?: string
  is_active?: string
  is_staff?: string
  subscription_plan?: string
  ordering?: string
} = {}): Promise<PaginatedResponse<AdminUser>> {
  const { data } = await api.get('/admin/users/', { params })
  return data
}

export async function fetchAdminUser(id: string): Promise<AdminUser> {
  const { data } = await api.get(`/admin/users/${id}/`)
  return data
}

export async function updateAdminUser(id: string, payload: Partial<AdminUser>): Promise<AdminUser> {
  const { data } = await api.patch(`/admin/users/${id}/`, payload)
  return data
}

export async function toggleUserActive(id: string): Promise<{ is_active: boolean }> {
  const { data } = await api.post(`/admin/users/${id}/toggle_active/`)
  return data
}

export async function toggleUserStaff(id: string): Promise<{ is_staff: boolean }> {
  const { data } = await api.post(`/admin/users/${id}/toggle_staff/`)
  return data
}

export async function deleteAdminUser(id: string): Promise<void> {
  await api.delete(`/admin/users/${id}/`)
}

export async function fetchAdminDocuments(params: {
  page?: number
  search?: string
  doc_type?: string
  is_deleted?: string
  ordering?: string
} = {}): Promise<PaginatedResponse<AdminDocument>> {
  const { data } = await api.get('/admin/documents/', { params })
  return data
}

export async function restoreAdminDocument(id: string): Promise<void> {
  await api.post(`/admin/documents/${id}/restore/`)
}

export async function deleteAdminDocument(id: string): Promise<void> {
  await api.delete(`/admin/documents/${id}/`)
}
