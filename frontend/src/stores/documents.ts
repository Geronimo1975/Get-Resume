import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import type { Document, DocType, PaginatedResponse } from '@/types'

export const useDocumentsStore = defineStore('documents', () => {
  const documents = ref<Document[]>([])
  const currentDocument = ref<Document | null>(null)
  const loading = ref(false)
  const filterType = ref<DocType | 'alle'>('alle')
  const sortBy = ref<'updated_at' | 'created_at' | 'title'>('updated_at')

  const filteredDocuments = computed(() => {
    let docs = [...documents.value]
    if (filterType.value !== 'alle') {
      docs = docs.filter((d) => d.doc_type === filterType.value)
    }
    docs.sort((a, b) => {
      if (sortBy.value === 'title') return a.title.localeCompare(b.title)
      return new Date(b[sortBy.value]).getTime() - new Date(a[sortBy.value]).getTime()
    })
    return docs
  })

  const documentCounts = computed(() => ({
    alle: documents.value.length,
    lebenslauf: documents.value.filter((d) => d.doc_type === 'lebenslauf').length,
    anschreiben: documents.value.filter((d) => d.doc_type === 'anschreiben').length,
    deckblatt: documents.value.filter((d) => d.doc_type === 'deckblatt').length,
  }))

  async function fetchDocuments() {
    loading.value = true
    try {
      const { data } = await api.get<PaginatedResponse<Document>>('/documents/')
      documents.value = data.results
    } finally {
      loading.value = false
    }
  }

  async function fetchDocument(id: string) {
    loading.value = true
    try {
      const { data } = await api.get<Document>(`/documents/${id}/`)
      currentDocument.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  async function createDocument(payload: { title: string; doc_type: DocType; template?: string }) {
    const { data } = await api.post<Document>('/documents/', payload)
    documents.value.unshift(data)
    return data
  }

  async function updateDocument(id: string, payload: Partial<Document>) {
    const { data } = await api.patch<Document>(`/documents/${id}/`, payload)
    currentDocument.value = data
    const idx = documents.value.findIndex((d) => d.id === id)
    if (idx !== -1) documents.value[idx] = data
    return data
  }

  async function deleteDocument(id: string) {
    await api.delete(`/documents/${id}/`)
    documents.value = documents.value.filter((d) => d.id !== id)
    if (currentDocument.value?.id === id) currentDocument.value = null
  }

  async function duplicateDocument(id: string) {
    const { data } = await api.post<Document>(`/documents/${id}/duplicate/`)
    documents.value.unshift(data)
    return data
  }

  return {
    documents,
    currentDocument,
    loading,
    filterType,
    sortBy,
    filteredDocuments,
    documentCounts,
    fetchDocuments,
    fetchDocument,
    createDocument,
    updateDocument,
    deleteDocument,
    duplicateDocument,
  }
})
