import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  fetchAdminStats,
  fetchAdminUsers,
  fetchAdminUser,
  toggleUserActive,
  toggleUserStaff,
  deleteAdminUser,
  fetchAdminDocuments,
  restoreAdminDocument,
  deleteAdminDocument,
  type AdminStats,
  type AdminUser,
  type AdminDocument,
} from '@/api/admin'

export const useAdminStore = defineStore('admin', () => {
  // State
  const stats = ref<AdminStats | null>(null)
  const users = ref<AdminUser[]>([])
  const userCount = ref(0)
  const documents = ref<AdminDocument[]>([])
  const documentCount = ref(0)
  const selectedUser = ref<AdminUser | null>(null)

  const loading = ref({
    stats: false,
    users: false,
    documents: false,
  })

  // Filters
  const userFilters = ref({
    page: 1,
    search: '',
    is_active: '',
    is_staff: '',
    subscription_plan: '',
  })

  const docFilters = ref({
    page: 1,
    search: '',
    doc_type: '',
    is_deleted: '',
  })

  // Computed
  const usersByPlan = computed(() => {
    if (!stats.value) return {}
    return stats.value.subscriptions
  })

  const totalPages = computed(() => ({
    users: Math.ceil(userCount.value / 20) || 1,
    documents: Math.ceil(documentCount.value / 20) || 1,
  }))

  // Actions
  async function loadStats() {
    loading.value.stats = true
    try {
      stats.value = await fetchAdminStats()
    } finally {
      loading.value.stats = false
    }
  }

  async function loadUsers() {
    loading.value.users = true
    try {
      const params: Record<string, string | number> = { page: userFilters.value.page }
      if (userFilters.value.search) params.search = userFilters.value.search
      if (userFilters.value.is_active) params.is_active = userFilters.value.is_active
      if (userFilters.value.is_staff) params.is_staff = userFilters.value.is_staff
      if (userFilters.value.subscription_plan) params.subscription_plan = userFilters.value.subscription_plan
      const res = await fetchAdminUsers(params)
      users.value = res.results
      userCount.value = res.count
    } finally {
      loading.value.users = false
    }
  }

  async function loadUser(id: string) {
    selectedUser.value = await fetchAdminUser(id)
  }

  async function toggleActive(id: string) {
    const res = await toggleUserActive(id)
    const user = users.value.find(u => u.id === id)
    if (user) user.is_active = res.is_active
    if (selectedUser.value?.id === id) selectedUser.value.is_active = res.is_active
  }

  async function toggleStaff(id: string) {
    const res = await toggleUserStaff(id)
    const user = users.value.find(u => u.id === id)
    if (user) user.is_staff = res.is_staff
    if (selectedUser.value?.id === id) selectedUser.value.is_staff = res.is_staff
  }

  async function deactivateUser(id: string) {
    await deleteAdminUser(id)
    const user = users.value.find(u => u.id === id)
    if (user) user.is_active = false
    if (selectedUser.value?.id === id) selectedUser.value.is_active = false
  }

  async function loadDocuments() {
    loading.value.documents = true
    try {
      const params: Record<string, string | number> = { page: docFilters.value.page }
      if (docFilters.value.search) params.search = docFilters.value.search
      if (docFilters.value.doc_type) params.doc_type = docFilters.value.doc_type
      if (docFilters.value.is_deleted) params.is_deleted = docFilters.value.is_deleted
      const res = await fetchAdminDocuments(params)
      documents.value = res.results
      documentCount.value = res.count
    } finally {
      loading.value.documents = false
    }
  }

  async function restoreDoc(id: string) {
    await restoreAdminDocument(id)
    const doc = documents.value.find(d => d.id === id)
    if (doc) doc.deleted_at = null
  }

  async function hardDeleteDoc(id: string) {
    await deleteAdminDocument(id)
    documents.value = documents.value.filter(d => d.id !== id)
    documentCount.value--
  }

  return {
    stats, users, userCount, documents, documentCount, selectedUser,
    loading, userFilters, docFilters,
    usersByPlan, totalPages,
    loadStats, loadUsers, loadUser, toggleActive, toggleStaff, deactivateUser,
    loadDocuments, restoreDoc, hardDeleteDoc,
  }
})
