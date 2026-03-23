<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { formatDateDE } from '@/lib/formatters'
import Badge from '@/components/ui/Badge.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'

const auth = useAuthStore()

const planNames: Record<string, string> = {
  free: 'Kostenlos',
  premium_monthly: 'Premium Monatlich',
  premium_yearly: 'Premium Jahrlich',
  business: 'Business',
}
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Aktueller Plan</h3>
    </CardHeader>
    <CardContent>
      <div class="flex items-center gap-3">
        <Badge :variant="auth.isPremium ? 'premium' : 'secondary'" class="text-sm">
          {{ planNames[auth.subscriptionPlan] || 'Kostenlos' }}
        </Badge>
        <span v-if="auth.user?.profile?.subscription_expires_at" class="text-sm text-muted-foreground">
          Gultig bis {{ formatDateDE(auth.user.profile.subscription_expires_at) }}
        </span>
      </div>
    </CardContent>
  </Card>
</template>
