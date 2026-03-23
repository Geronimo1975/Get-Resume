import api from './client'
import type { SubscriptionInfo, Invoice, SubscriptionPlan } from '@/types'

export function fetchSubscription() {
  return api.get<SubscriptionInfo>('/payments/subscription/')
}

export function createCheckout(plan: SubscriptionPlan) {
  return api.post<{ checkout_url: string }>('/payments/checkout/', { plan })
}

export function cancelSubscription() {
  return api.post('/payments/subscription/cancel/')
}

export function fetchInvoices() {
  return api.get<Invoice[]>('/payments/invoices/')
}
