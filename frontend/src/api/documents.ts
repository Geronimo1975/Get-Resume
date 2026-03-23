import api from './client'
import type { Document, PaginatedResponse, DocType } from '@/types'

export function fetchDocuments(params?: { doc_type?: DocType; ordering?: string }) {
  return api.get<PaginatedResponse<Document>>('/documents/', { params })
}

export function fetchDocument(id: string) {
  return api.get<Document>(`/documents/${id}/`)
}

export function createDocument(payload: { title: string; doc_type: DocType; template?: string }) {
  return api.post<Document>('/documents/', payload)
}

export function updateDocument(id: string, payload: Partial<Document>) {
  return api.patch<Document>(`/documents/${id}/`, payload)
}

export function deleteDocument(id: string) {
  return api.delete(`/documents/${id}/`)
}

export function duplicateDocument(id: string) {
  return api.post<Document>(`/documents/${id}/duplicate/`)
}

export function exportDocumentPdf(id: string) {
  return api.get(`/documents/${id}/export-pdf/`, { responseType: 'blob' })
}
