<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { RefreshCw } from 'lucide-vue-next'
import Tabs from '@/components/ui/Tabs.vue'
import AdminOverview from '@/components/admin/AdminOverview.vue'
import AdminUsers from '@/components/admin/AdminUsers.vue'
import AdminDocuments from '@/components/admin/AdminDocuments.vue'
import AdminRevenue from '@/components/admin/AdminRevenue.vue'
import AdminSystem from '@/components/admin/AdminSystem.vue'

const store = useAdminStore()
const activeTab = ref('overview')
const lastRefresh = ref(new Date())

// Live clock
const now = ref(new Date())
let clockInterval: ReturnType<typeof setInterval>

const clockDisplay = computed(() =>
  now.value.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
)
const dateDisplay = computed(() =>
  now.value.toLocaleDateString('de-DE', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
)

const tabs = computed(() => [
  { value: 'overview', label: 'Übersicht' },
  { value: 'users', label: 'Benutzer', count: store.stats?.users.total },
  { value: 'documents', label: 'Dokumente', count: store.stats?.documents.total },
  { value: 'revenue', label: 'Einnahmen' },
  { value: 'system', label: 'System' },
])

async function refresh() {
  await store.loadStats()
  lastRefresh.value = new Date()
}

onMounted(() => {
  store.loadStats()
  clockInterval = setInterval(() => { now.value = new Date() }, 1000)
})

onUnmounted(() => {
  clearInterval(clockInterval)
})
</script>

<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <div class="relative mb-6">
      <div class="absolute inset-0 overflow-hidden pointer-events-none rounded-2xl">
        <div class="scan-line"></div>
      </div>

      <div class="relative rounded-2xl border border-emerald-500/10 bg-gradient-to-br from-[#0a0f0d] via-[#0d1210] to-[#0a0f0d] p-6 overflow-hidden">
        <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-48 h-48 bg-cyan-500/5 rounded-full blur-3xl"></div>
        <div class="absolute inset-0 opacity-20" style="background-image: linear-gradient(rgba(16,185,129,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(16,185,129,0.06) 1px, transparent 1px); background-size: 32px 32px;"></div>

        <div class="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <div class="flex items-center gap-2">
                <div class="relative">
                  <div class="h-2.5 w-2.5 rounded-full bg-emerald-500"></div>
                  <div class="absolute inset-0 h-2.5 w-2.5 rounded-full bg-emerald-500 animate-ping opacity-75"></div>
                </div>
                <span class="font-mono text-xs tracking-widest text-emerald-500/80 uppercase">System Online</span>
              </div>
              <span class="text-zinc-700 font-mono text-xs">|</span>
              <span class="font-mono text-xs text-zinc-600">v1.0.0</span>
            </div>
            <h1 class="text-2xl lg:text-3xl font-bold tracking-tight">
              <span class="text-foreground">Admin</span>
              <span class="text-emerald-400"> Zentrale</span>
            </h1>
            <p class="text-sm text-zinc-500 mt-1 font-mono">{{ dateDisplay }}</p>
          </div>

          <div class="flex items-center gap-4">
            <div class="hidden lg:flex flex-col items-end">
              <div class="font-mono text-3xl font-bold tracking-wider text-emerald-400/90 tabular-nums">
                {{ clockDisplay }}
              </div>
              <span class="font-mono text-[10px] text-zinc-600 tracking-widest uppercase mt-0.5">Europe/Berlin</span>
            </div>
            <button
              @click="refresh"
              :class="[
                'flex items-center gap-2 px-3 py-2 rounded-lg font-mono text-xs border transition-all duration-300',
                'border-emerald-500/20 text-emerald-400/70 hover:text-emerald-400 hover:bg-emerald-500/5 hover:border-emerald-500/30'
              ]"
            >
              <RefreshCw :class="['h-3.5 w-3.5', store.loading.stats ? 'animate-spin' : '']" />
              Aktualisieren
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="mb-6">
      <Tabs v-model="activeTab" :tabs="tabs" />
    </div>

    <!-- Tab Content -->
    <AdminOverview v-if="activeTab === 'overview'" />
    <AdminUsers v-else-if="activeTab === 'users'" />
    <AdminDocuments v-else-if="activeTab === 'documents'" />
    <AdminRevenue v-else-if="activeTab === 'revenue'" />
    <AdminSystem v-else-if="activeTab === 'system'" />

    <!-- Footer -->
    <div class="mt-6 flex items-center justify-between text-[10px] font-mono text-zinc-700">
      <span>GetResume Admin v1.0.0 // resume.get-hub.io</span>
      <span>Letzte Aktualisierung: {{ lastRefresh.toLocaleTimeString('de-DE') }}</span>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard {
  animation: fade-in 0.4s ease-out;
}
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.scan-line {
  position: absolute;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.15), transparent);
  animation: scan 4s linear infinite;
  pointer-events: none;
}
@keyframes scan {
  0% { top: -2px; }
  100% { top: 100%; }
}
</style>
