<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { createCheckout } from '@/api/payments'
import type { SubscriptionPlan } from '@/types'
import PageHeader from '@/components/shared/PageHeader.vue'
import CurrentPlan from '@/components/billing/CurrentPlan.vue'
import PricingTable from '@/components/billing/PricingTable.vue'
import InvoiceList from '@/components/billing/InvoiceList.vue'

const auth = useAuthStore()
const { toast } = useToast()

async function handleSelectPlan(planId: string) {
  if (planId === 'free') return
  try {
    const { data } = await createCheckout(planId as SubscriptionPlan)
    window.location.href = data.checkout_url
  } catch {
    toast({ title: 'Fehler', description: 'Checkout konnte nicht gestartet werden.', variant: 'destructive' })
  }
}
</script>

<template>
  <div>
    <PageHeader title="Abonnement" description="Verwalten Sie Ihren Plan und Ihre Rechnungen" />

    <div class="space-y-8">
      <CurrentPlan />

      <div>
        <h2 class="text-lg font-semibold text-foreground mb-4">Plan wechseln</h2>
        <PricingTable
          :current-plan="auth.subscriptionPlan"
          @select="handleSelectPlan"
        />
      </div>

      <InvoiceList />
    </div>
  </div>
</template>
