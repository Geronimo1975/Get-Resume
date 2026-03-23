<script setup lang="ts">
import Badge from '@/components/ui/Badge.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const planLabels: Record<string, string> = {
  free: 'Free',
  premium_monthly: 'Premium',
  premium_yearly: 'Premium',
  business: 'Business',
}
</script>

<template>
  <Badge :variant="auth.isPremium ? 'premium' : 'secondary'" class="text-xs">
    {{ planLabels[auth.subscriptionPlan] || 'Free' }}
  </Badge>
</template>
