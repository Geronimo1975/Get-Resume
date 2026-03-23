import axios from 'axios'
import type { AuthTokens } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT access token to every request
api.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('tokens')
  if (tokens) {
    const { access } = JSON.parse(tokens) as AuthTokens
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const tokens = localStorage.getItem('tokens')
      if (tokens) {
        try {
          const { refresh } = JSON.parse(tokens) as AuthTokens
          const { data } = await axios.post('/api/v1/auth/token/refresh/', { refresh })
          const newTokens: AuthTokens = { access: data.access, refresh: data.refresh ?? refresh }
          localStorage.setItem('tokens', JSON.stringify(newTokens))
          original.headers.Authorization = `Bearer ${newTokens.access}`
          return api(original)
        } catch {
          localStorage.removeItem('tokens')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  },
)

export default api
