<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { ArrowLeft, Shield, CheckCircle2, Star } from 'lucide-vue-next'
import PricingTable from '@/components/billing/PricingTable.vue'
import Button from '@/components/ui/Button.vue'

const router = useRouter()

function selectPlan(_planId: string) {
  router.push('/register')
}
</script>

<template>
  <div class="min-h-screen bg-background relative overflow-hidden">
    <!-- Background -->
    <div class="absolute inset-0 bg-dots opacity-30"></div>
    <div class="absolute top-1/4 left-1/4 h-[500px] w-[500px] rounded-full bg-indigo-500/[0.06] blur-[120px]"></div>
    <div class="absolute bottom-1/4 right-1/4 h-[400px] w-[400px] rounded-full bg-violet-500/[0.05] blur-[120px]"></div>

    <!-- Header -->
    <header class="sticky top-0 z-50 glass border-b border-white/[0.06]">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <RouterLink to="/" class="flex items-center gap-2.5 group">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 font-mono text-sm font-bold text-indigo-400">&gt;_</div>
          <span class="text-lg font-semibold text-foreground">Get<span class="text-indigo-400">Resume</span></span>
        </RouterLink>
        <nav class="flex items-center gap-6">
          <RouterLink to="/login" class="text-sm text-zinc-400 hover:text-foreground transition-colors">Anmelden</RouterLink>
          <RouterLink to="/register">
            <Button size="sm" class="glow-sm">Kostenlos starten</Button>
          </RouterLink>
        </nav>
      </div>
    </header>

    <div class="relative mx-auto max-w-6xl px-4 py-20">
      <div class="text-center mb-16 animate-fade-in">
        <div class="inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/5 px-4 py-1.5 text-sm font-mono text-indigo-400 mb-4">
          <Star class="h-3.5 w-3.5" />
          Preise
        </div>
        <h1 class="font-mono text-4xl lg:text-5xl font-bold tracking-tight">
          Faire, <span class="text-gradient">transparente</span> Preise
        </h1>
        <p class="mt-4 text-lg text-zinc-400 max-w-2xl mx-auto">
          Alle Preise inkl. 19% MwSt gemafl PAngV. Keine versteckten Kosten.
        </p>
      </div>

      <div class="animate-fade-in-up">
        <PricingTable @select="selectPlan" />
      </div>

      <!-- Trust badges -->
      <div class="mt-16 flex flex-wrap items-center justify-center gap-4 animate-fade-in-up-delayed">
        <div class="flex items-center gap-2.5 rounded-xl border border-white/[0.06] bg-card/50 px-4 py-2.5 text-sm text-zinc-300 font-mono">
          <Shield class="h-4 w-4 text-emerald-400" />
          14-Tage Widerrufsrecht
        </div>
        <div class="flex items-center gap-2.5 rounded-xl border border-white/[0.06] bg-card/50 px-4 py-2.5 text-sm text-zinc-300 font-mono">
          <CheckCircle2 class="h-4 w-4 text-emerald-400" />
          Jederzeit kundbar
        </div>
        <div class="flex items-center gap-2.5 rounded-xl border border-white/[0.06] bg-card/50 px-4 py-2.5 text-sm text-zinc-300 font-mono">
          <Shield class="h-4 w-4 text-emerald-400" />
          DSGVO-konform
        </div>
      </div>

      <div class="mt-10 text-center">
        <RouterLink to="/" class="inline-flex items-center gap-1.5 text-sm text-indigo-400 hover:text-indigo-300 font-mono transition-colors">
          <ArrowLeft class="h-3.5 w-3.5" />
          Zuruck zur Startseite
        </RouterLink>
      </div>
    </div>
  </div>
</template>
