import api from './client'
import type { Template, PaginatedResponse, TemplateCategory } from '@/types'

export function fetchTemplates(params?: { category?: TemplateCategory }) {
  return api.get<PaginatedResponse<Template>>('/documents/templates/', { params })
}

export function fetchTemplate(id: string) {
  return api.get<Template>(`/documents/templates/${id}/`)
}
