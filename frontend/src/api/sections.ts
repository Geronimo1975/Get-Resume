import api from './client'
import type { Section, SectionType } from '@/types'

export function createSection(documentId: string, payload: {
  section_type: SectionType
  title: string
  content?: Record<string, unknown>
  ordering?: number
}) {
  return api.post<Section>(`/documents/${documentId}/sections/`, payload)
}

export function updateSection(documentId: string, sectionId: string, payload: Partial<Section>) {
  return api.patch<Section>(`/documents/${documentId}/sections/${sectionId}/`, payload)
}

export function deleteSection(documentId: string, sectionId: string) {
  return api.delete(`/documents/${documentId}/sections/${sectionId}/`)
}

export function reorderSections(documentId: string, ordering: { id: string; ordering: number }[]) {
  return api.post(`/documents/${documentId}/sections/reorder/`, { ordering })
}
