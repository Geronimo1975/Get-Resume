import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import type { User, UserProfile, AuthTokens } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(loadTokens())

  const isAuthenticated = computed(() => !!tokens.value?.access)
  const subscriptionPlan = computed(() => user.value?.profile?.subscription_plan ?? 'free')
  const isPremium = computed(() => {
    const plan = subscriptionPlan.value
    return plan === 'premium_monthly' || plan === 'premium_yearly' || plan === 'business'
  })
  const isStaff = computed(() => !!user.value?.is_staff)
  const userInitials = computed(() => {
    const f = user.value?.first_name?.[0] ?? ''
    const l = user.value?.last_name?.[0] ?? ''
    return (f + l).toUpperCase() || '?'
  })

  function loadTokens(): AuthTokens | null {
    const stored = localStorage.getItem('tokens')
    return stored ? JSON.parse(stored) : null
  }

  function saveTokens(t: AuthTokens) {
    tokens.value = t
    localStorage.setItem('tokens', JSON.stringify(t))
  }

  function clearAuth() {
    user.value = null
    tokens.value = null
    localStorage.removeItem('tokens')
  }

  async function login(email: string, password: string) {
    const { data } = await api.post('/auth/login/', { email, password })
    saveTokens({ access: data.access, refresh: data.refresh })
    await fetchUser()
  }

  async function register(payload: {
    email: string
    password1: string
    password2: string
    first_name: string
    last_name: string
  }): Promise<'verified' | 'verification_sent'> {
    const { data, status } = await api.post('/auth/registration/', payload)
    if (data?.access) {
      saveTokens({ access: data.access, refresh: data.refresh })
      await fetchUser()
      return 'verified'
    }
    // 204 or response without tokens = email verification required
    return 'verification_sent'
  }

  async function logout() {
    try {
      await api.post('/auth/logout/')
    } finally {
      clearAuth()
    }
  }

  async function fetchUser() {
    const { data } = await api.get('/users/me/')
    user.value = data
  }

  async function updateProfile(payload: Partial<UserProfile>) {
    const { data } = await api.patch('/users/me/profile/', payload)
    if (user.value) {
      user.value.profile = data
    }
  }

  async function resendVerification(email: string) {
    await api.post('/auth/registration/resend-email/', { email })
  }

  async function init() {
    if (tokens.value?.access) {
      try {
        await fetchUser()
      } catch {
        clearAuth()
      }
    }
  }

  return {
    user,
    tokens,
    isAuthenticated,
    subscriptionPlan,
    isPremium,
    isStaff,
    userInitials,
    login,
    register,
    logout,
    fetchUser,
    resendVerification,
    updateProfile,
    init,
  }
})
