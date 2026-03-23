<script setup lang="ts">
import { computed } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { formatRelativeDE } from '@/lib/formatters'
import {
  Users, FileText, Crown, Activity, Database,
  Zap, ArrowUpRight, UserPlus, FilePlus,
} from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Skeleton from '@/components/ui/Skeleton.vue'

const store = useAdminStore()

const premiumRate = computed(() => {
  if (!store.stats || store.stats.users.total === 0) return 0
  return Math.round((store.stats.users.premium / store.stats.users.total) * 100)
})
</script>

<template>
  <!-- Stat Cards -->
  <div v-if="store.loading.stats" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
    <Skeleton v-for="i in 4" :key="i" class="h-36 w-full rounded-xl" />
  </div>

  <div v-else-if="store.stats" class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      <!-- Users Total -->
      <div class="stat-card group">
        <div class="stat-card-glow bg-emerald-500/5"></div>
        <div class="relative p-5">
          <div class="flex items-center justify-between mb-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <Users class="h-5 w-5 text-emerald-400" />
            </div>
            <div class="flex items-center gap-1 text-emerald-400">
              <ArrowUpRight class="h-3.5 w-3.5" />
              <span class="font-mono text-xs font-semibold">+{{ store.stats.users.new_today }}</span>
            </div>
          </div>
          <div class="font-mono text-3xl font-bold text-foreground tracking-tight">{{ store.stats.users.total }}</div>
          <div class="flex items-center justify-between mt-1">
            <span class="text-xs text-zinc-500">Benutzer gesamt</span>
            <span class="font-mono text-[10px] text-zinc-600">{{ store.stats.users.active_30d }} aktiv</span>
          </div>
          <div class="mt-3 h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div class="h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-1000" :style="{ width: store.stats.users.total > 0 ? '100%' : '0%' }"></div>
          </div>
        </div>
      </div>

      <!-- Documents Total -->
      <div class="stat-card group">
        <div class="stat-card-glow bg-cyan-500/5"></div>
        <div class="relative p-5">
          <div class="flex items-center justify-between mb-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20">
              <FileText class="h-5 w-5 text-cyan-400" />
            </div>
            <div class="flex items-center gap-1 text-cyan-400">
              <ArrowUpRight class="h-3.5 w-3.5" />
              <span class="font-mono text-xs font-semibold">+{{ store.stats.documents.created_today }}</span>
            </div>
          </div>
          <div class="font-mono text-3xl font-bold text-foreground tracking-tight">{{ store.stats.documents.total }}</div>
          <div class="flex items-center justify-between mt-1">
            <span class="text-xs text-zinc-500">Dokumente gesamt</span>
            <span class="font-mono text-[10px] text-zinc-600">{{ store.stats.documents.created_7d }} / 7 Tage</span>
          </div>
          <div class="mt-3 flex gap-1 h-1">
            <div class="rounded-full bg-cyan-500 transition-all duration-1000" :style="{ flexGrow: store.stats.documents.by_type.lebenslauf || 1 }"></div>
            <div class="rounded-full bg-cyan-400/50 transition-all duration-1000" :style="{ flexGrow: store.stats.documents.by_type.anschreiben || 0.3 }"></div>
            <div class="rounded-full bg-cyan-300/30 transition-all duration-1000" :style="{ flexGrow: store.stats.documents.by_type.deckblatt || 0.1 }"></div>
          </div>
        </div>
      </div>

      <!-- Premium Users -->
      <div class="stat-card group">
        <div class="stat-card-glow bg-amber-500/5"></div>
        <div class="relative p-5">
          <div class="flex items-center justify-between mb-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/20">
              <Crown class="h-5 w-5 text-amber-400" />
            </div>
            <Badge class="bg-amber-500/10 text-amber-400 border-amber-500/20 font-mono text-[10px]">
              {{ premiumRate }}%
            </Badge>
          </div>
          <div class="font-mono text-3xl font-bold text-foreground tracking-tight">{{ store.stats.users.premium }}</div>
          <div class="flex items-center justify-between mt-1">
            <span class="text-xs text-zinc-500">Premium Nutzer</span>
            <span class="font-mono text-[10px] text-zinc-600">{{ store.stats.users.free }} kostenlos</span>
          </div>
          <div class="mt-3 h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div class="h-full rounded-full bg-gradient-to-r from-amber-500 to-amber-400 transition-all duration-1000" :style="{ width: premiumRate + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- System Health -->
      <div class="stat-card group">
        <div class="stat-card-glow bg-violet-500/5"></div>
        <div class="relative p-5">
          <div class="flex items-center justify-between mb-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/10 border border-violet-500/20">
              <Activity class="h-5 w-5 text-violet-400" />
            </div>
            <div class="flex items-center gap-1.5">
              <div class="h-2 w-2 rounded-full bg-emerald-500"></div>
              <span class="font-mono text-[10px] text-emerald-400">Gesund</span>
            </div>
          </div>
          <div class="font-mono text-lg font-bold text-foreground tracking-tight">{{ store.stats.system.uptime }}</div>
          <div class="flex items-center justify-between mt-1">
            <span class="text-xs text-zinc-500">Betriebszeit</span>
          </div>
          <div class="mt-3 grid grid-cols-2 gap-2">
            <div class="flex items-center gap-1.5">
              <Database class="h-3 w-3 text-zinc-600" />
              <span class="font-mono text-[10px] text-zinc-500">{{ store.stats.system.db_size }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <Zap class="h-3 w-3 text-zinc-600" />
              <span class="font-mono text-[10px] text-zinc-500">{{ store.stats.system.redis_memory }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity Panels -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Recent Signups -->
      <div class="rounded-xl border border-white/[0.06] bg-card overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-white/[0.04]">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <UserPlus class="h-4 w-4 text-emerald-400" />
            </div>
            <div>
              <h3 class="text-sm font-semibold text-foreground">Neue Registrierungen</h3>
              <p class="text-[10px] font-mono text-zinc-600 uppercase tracking-wider">Letzte Anmeldungen</p>
            </div>
          </div>
          <Badge class="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 font-mono text-[10px]">Live</Badge>
        </div>
        <div class="divide-y divide-white/[0.03]">
          <template v-if="store.stats.recent_signups.length > 0">
            <div
              v-for="user in store.stats.recent_signups.slice(0, 6)"
              :key="user.id"
              class="flex items-center gap-3 px-5 py-3 hover:bg-white/[0.02] transition-colors"
            >
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700 text-xs font-mono font-bold text-zinc-400 shrink-0">
                {{ (user.first_name?.[0] || '') + (user.last_name?.[0] || '') || '?' }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-foreground truncate">{{ user.first_name }} {{ user.last_name }}</p>
                <p class="text-[11px] font-mono text-zinc-600 truncate">{{ user.email }}</p>
              </div>
              <span class="text-[10px] font-mono text-zinc-600 shrink-0">{{ formatRelativeDE(user.date_joined) }}</span>
            </div>
          </template>
          <div v-else class="px-5 py-12 text-center">
            <Users class="h-8 w-8 text-zinc-700 mx-auto mb-3" />
            <p class="text-sm text-zinc-500">Noch keine Registrierungen</p>
          </div>
        </div>
      </div>

      <!-- Recent Documents -->
      <div class="rounded-xl border border-white/[0.06] bg-card overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-white/[0.04]">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <FilePlus class="h-4 w-4 text-cyan-400" />
            </div>
            <div>
              <h3 class="text-sm font-semibold text-foreground">Neueste Dokumente</h3>
              <p class="text-[10px] font-mono text-zinc-600 uppercase tracking-wider">Letzte Erstellungen</p>
            </div>
          </div>
          <Badge class="bg-cyan-500/10 text-cyan-400 border-cyan-500/20 font-mono text-[10px]">Live</Badge>
        </div>
        <div class="divide-y divide-white/[0.03]">
          <template v-if="store.stats.recent_documents.length > 0">
            <div
              v-for="doc in store.stats.recent_documents.slice(0, 6)"
              :key="doc.id"
              class="flex items-center gap-3 px-5 py-3 hover:bg-white/[0.02] transition-colors"
            >
              <div :class="[
                'flex h-8 w-8 items-center justify-center rounded-lg border shrink-0',
                doc.doc_type === 'lebenslauf' ? 'bg-cyan-500/10 border-cyan-500/20' :
                doc.doc_type === 'anschreiben' ? 'bg-violet-500/10 border-violet-500/20' :
                'bg-amber-500/10 border-amber-500/20'
              ]">
                <FileText :class="[
                  'h-4 w-4',
                  doc.doc_type === 'lebenslauf' ? 'text-cyan-400' :
                  doc.doc_type === 'anschreiben' ? 'text-violet-400' :
                  'text-amber-400'
                ]" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-foreground truncate">{{ doc.title }}</p>
                <p class="text-[11px] font-mono text-zinc-600 truncate">{{ doc.user_email }}</p>
              </div>
              <Badge :class="[
                'text-[10px] font-mono border',
                doc.doc_type === 'lebenslauf' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' :
                doc.doc_type === 'anschreiben' ? 'bg-violet-500/10 text-violet-400 border-violet-500/20' :
                'bg-amber-500/10 text-amber-400 border-amber-500/20'
              ]">
                {{ doc.doc_type }}
              </Badge>
            </div>
          </template>
          <div v-else class="px-5 py-12 text-center">
            <FileText class="h-8 w-8 text-zinc-700 mx-auto mb-3" />
            <p class="text-sm text-zinc-500">Noch keine Dokumente</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Subscription Breakdown -->
    <div class="rounded-xl border border-white/[0.06] bg-card overflow-hidden">
      <div class="px-5 py-4 border-b border-white/[0.04]">
        <h3 class="text-sm font-semibold text-foreground">Abo-Verteilung</h3>
        <p class="text-[10px] font-mono text-zinc-600 uppercase tracking-wider">Benutzer nach Tarif</p>
      </div>
      <div class="grid grid-cols-2 lg:grid-cols-4 divide-x divide-white/[0.04]">
        <div class="p-5 text-center">
          <div class="font-mono text-2xl font-bold text-foreground">{{ store.stats.subscriptions.free }}</div>
          <div class="text-xs text-zinc-500 mt-1">Kostenlos</div>
          <div class="mt-2 h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div class="h-full rounded-full bg-zinc-500" :style="{ width: store.stats.users.total ? (store.stats.subscriptions.free / store.stats.users.total * 100) + '%' : '0%' }"></div>
          </div>
        </div>
        <div class="p-5 text-center">
          <div class="font-mono text-2xl font-bold text-amber-400">{{ store.stats.subscriptions.premium_monthly }}</div>
          <div class="text-xs text-zinc-500 mt-1">Premium Monatlich</div>
          <div class="mt-2 h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div class="h-full rounded-full bg-amber-500" :style="{ width: store.stats.users.total ? (store.stats.subscriptions.premium_monthly / store.stats.users.total * 100) + '%' : '0%' }"></div>
          </div>
        </div>
        <div class="p-5 text-center">
          <div class="font-mono text-2xl font-bold text-amber-400">{{ store.stats.subscriptions.premium_yearly }}</div>
          <div class="text-xs text-zinc-500 mt-1">Premium Jährlich</div>
          <div class="mt-2 h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div class="h-full rounded-full bg-amber-400" :style="{ width: store.stats.users.total ? (store.stats.subscriptions.premium_yearly / store.stats.users.total * 100) + '%' : '0%' }"></div>
          </div>
        </div>
        <div class="p-5 text-center">
          <div class="font-mono text-2xl font-bold text-violet-400">{{ store.stats.subscriptions.business }}</div>
          <div class="text-xs text-zinc-500 mt-1">Business</div>
          <div class="mt-2 h-1 w-full rounded-full bg-zinc-800 overflow-hidden">
            <div class="h-full rounded-full bg-violet-500" :style="{ width: store.stats.users.total ? (store.stats.subscriptions.business / store.stats.users.total * 100) + '%' : '0%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  position: relative;
  overflow: hidden;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: var(--color-card);
  transition: all 0.3s ease;
}
.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}
.stat-card-glow {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: inherit;
}
.stat-card:hover .stat-card-glow {
  opacity: 1;
}
</style>
