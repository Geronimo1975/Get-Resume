<script setup lang="ts">
import { computed } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { Crown, TrendingUp, CreditCard, AlertCircle } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'

const store = useAdminStore()

const conversionRate = computed(() => {
  if (!store.stats || store.stats.users.total === 0) return '0.0'
  return ((store.stats.users.premium / store.stats.users.total) * 100).toFixed(1)
})

const totalPremium = computed(() => {
  if (!store.stats) return 0
  return store.stats.subscriptions.premium_monthly +
    store.stats.subscriptions.premium_yearly +
    store.stats.subscriptions.business
})
</script>

<template>
  <div v-if="store.stats" class="space-y-4">
    <!-- Subscription Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <!-- Free -->
      <div class="rounded-xl border border-white/[0.06] bg-card p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs text-zinc-500 uppercase tracking-wider font-mono">Kostenlos</span>
          <Badge class="bg-zinc-800 text-zinc-400 border-zinc-700 font-mono text-[10px]">
            {{ store.stats.users.total ? Math.round((store.stats.subscriptions.free / store.stats.users.total) * 100) : 0 }}%
          </Badge>
        </div>
        <div class="font-mono text-3xl font-bold text-foreground">{{ store.stats.subscriptions.free }}</div>
        <div class="mt-3 h-1.5 w-full rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-zinc-600 transition-all duration-1000"
            :style="{ width: store.stats.users.total ? (store.stats.subscriptions.free / store.stats.users.total * 100) + '%' : '0%' }">
          </div>
        </div>
      </div>

      <!-- Premium Monthly -->
      <div class="rounded-xl border border-amber-500/10 bg-card p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs text-amber-400/70 uppercase tracking-wider font-mono">Premium Monatlich</span>
          <Crown class="h-4 w-4 text-amber-400" />
        </div>
        <div class="font-mono text-3xl font-bold text-amber-400">{{ store.stats.subscriptions.premium_monthly }}</div>
        <div class="mt-3 h-1.5 w-full rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-amber-500 transition-all duration-1000"
            :style="{ width: store.stats.users.total ? (store.stats.subscriptions.premium_monthly / store.stats.users.total * 100) + '%' : '0%' }">
          </div>
        </div>
      </div>

      <!-- Premium Yearly -->
      <div class="rounded-xl border border-amber-500/10 bg-card p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs text-amber-400/70 uppercase tracking-wider font-mono">Premium Jährlich</span>
          <Crown class="h-4 w-4 text-amber-400" />
        </div>
        <div class="font-mono text-3xl font-bold text-amber-400">{{ store.stats.subscriptions.premium_yearly }}</div>
        <div class="mt-3 h-1.5 w-full rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-amber-400 transition-all duration-1000"
            :style="{ width: store.stats.users.total ? (store.stats.subscriptions.premium_yearly / store.stats.users.total * 100) + '%' : '0%' }">
          </div>
        </div>
      </div>

      <!-- Business -->
      <div class="rounded-xl border border-violet-500/10 bg-card p-5">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs text-violet-400/70 uppercase tracking-wider font-mono">Business</span>
          <Crown class="h-4 w-4 text-violet-400" />
        </div>
        <div class="font-mono text-3xl font-bold text-violet-400">{{ store.stats.subscriptions.business }}</div>
        <div class="mt-3 h-1.5 w-full rounded-full bg-zinc-800 overflow-hidden">
          <div class="h-full rounded-full bg-violet-500 transition-all duration-1000"
            :style="{ width: store.stats.users.total ? (store.stats.subscriptions.business / store.stats.users.total * 100) + '%' : '0%' }">
          </div>
        </div>
      </div>
    </div>

    <!-- Conversion Metrics -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="rounded-xl border border-white/[0.06] bg-card p-5">
        <div class="flex items-center gap-2 mb-2">
          <TrendingUp class="h-4 w-4 text-emerald-400" />
          <span class="text-xs text-zinc-500 uppercase tracking-wider font-mono">Konversionsrate</span>
        </div>
        <div class="font-mono text-4xl font-bold text-emerald-400">{{ conversionRate }}%</div>
        <p class="text-xs text-zinc-500 mt-2">Free → Premium</p>
      </div>

      <div class="rounded-xl border border-white/[0.06] bg-card p-5">
        <div class="flex items-center gap-2 mb-2">
          <Crown class="h-4 w-4 text-amber-400" />
          <span class="text-xs text-zinc-500 uppercase tracking-wider font-mono">Zahlende Nutzer</span>
        </div>
        <div class="font-mono text-4xl font-bold text-foreground">{{ totalPremium }}</div>
        <p class="text-xs text-zinc-500 mt-2">Aktive Abonnements</p>
      </div>

      <div class="rounded-xl border border-white/[0.06] bg-card p-5">
        <div class="flex items-center gap-2 mb-2">
          <CreditCard class="h-4 w-4 text-cyan-400" />
          <span class="text-xs text-zinc-500 uppercase tracking-wider font-mono">MRR</span>
        </div>
        <div class="font-mono text-4xl font-bold text-zinc-600">—</div>
        <p class="text-xs text-zinc-500 mt-2">Stripe-Integration ausstehend</p>
      </div>
    </div>

    <!-- Stripe notice -->
    <div class="rounded-xl border border-amber-500/10 bg-amber-500/5 p-5 flex items-start gap-3">
      <AlertCircle class="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
      <div>
        <h4 class="text-sm font-semibold text-amber-400">Stripe-Integration ausstehend</h4>
        <p class="text-xs text-zinc-400 mt-1">
          Die tatsächlichen Einnahmen (MRR, Churn, LTV) werden nach der Stripe-Integration hier angezeigt.
          Aktuell werden nur die Abo-Pläne aus den Nutzerprofilen gezählt.
        </p>
      </div>
    </div>
  </div>
</template>
