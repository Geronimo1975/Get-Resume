<script setup lang="ts">
import { useAdminStore } from '@/stores/admin'
import { Database, Zap, Cpu, Server, Terminal } from 'lucide-vue-next'

const store = useAdminStore()
</script>

<template>
  <div v-if="store.stats" class="space-y-4">
    <!-- Infrastructure Status -->
    <div class="rounded-xl border border-white/[0.06] bg-card overflow-hidden">
      <div class="flex items-center gap-3 px-5 py-4 border-b border-white/[0.04]">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-800 border border-zinc-700">
          <Terminal class="h-4 w-4 text-zinc-400" />
        </div>
        <div>
          <h3 class="text-sm font-semibold text-foreground">Infrastruktur</h3>
          <p class="text-[10px] font-mono text-zinc-600 uppercase tracking-wider">Dienste & Verbindungen</p>
        </div>
      </div>

      <div class="grid grid-cols-2 lg:grid-cols-4 divide-x divide-white/[0.04]">
        <!-- PostgreSQL -->
        <div class="p-5">
          <div class="flex items-center gap-2 mb-3">
            <Database class="h-4 w-4 text-emerald-400" />
            <span class="font-mono text-xs text-zinc-400">PostgreSQL 16</span>
          </div>
          <div class="flex items-center gap-2 mb-2">
            <div class="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
            <span class="font-mono text-xs text-emerald-400">Verbunden</span>
          </div>
          <p class="font-mono text-[10px] text-zinc-600">Größe: {{ store.stats.system.db_size }}</p>
          <p class="font-mono text-[10px] text-zinc-600 mt-0.5">DB: lebenslauf_db</p>
        </div>

        <!-- Redis -->
        <div class="p-5">
          <div class="flex items-center gap-2 mb-3">
            <Zap class="h-4 w-4 text-red-400" />
            <span class="font-mono text-xs text-zinc-400">Redis 7</span>
          </div>
          <div class="flex items-center gap-2 mb-2">
            <div class="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
            <span class="font-mono text-xs text-emerald-400">Aktiv</span>
          </div>
          <p class="font-mono text-[10px] text-zinc-600">RAM: {{ store.stats.system.redis_memory }}</p>
          <p class="font-mono text-[10px] text-zinc-600 mt-0.5">4 Datenbanken (Cache, Sessions, Broker, Results)</p>
        </div>

        <!-- Celery -->
        <div class="p-5">
          <div class="flex items-center gap-2 mb-3">
            <Cpu class="h-4 w-4 text-violet-400" />
            <span class="font-mono text-xs text-zinc-400">Celery</span>
          </div>
          <div class="flex items-center gap-2 mb-2">
            <div class="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
            <span class="font-mono text-xs text-emerald-400">Worker bereit</span>
          </div>
          <p class="font-mono text-[10px] text-zinc-600">Queues: payments, gdpr, emails, default</p>
          <p class="font-mono text-[10px] text-zinc-600 mt-0.5">Beat: Scheduler aktiv</p>
        </div>

        <!-- Nginx + Traefik -->
        <div class="p-5">
          <div class="flex items-center gap-2 mb-3">
            <Server class="h-4 w-4 text-cyan-400" />
            <span class="font-mono text-xs text-zinc-400">Nginx + Traefik</span>
          </div>
          <div class="flex items-center gap-2 mb-2">
            <div class="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
            <span class="font-mono text-xs text-emerald-400">SSL aktiv</span>
          </div>
          <p class="font-mono text-[10px] text-zinc-600">TLS 1.3 / Let's Encrypt</p>
          <p class="font-mono text-[10px] text-zinc-600 mt-0.5">resume.get-hub.io</p>
        </div>
      </div>
    </div>

    <!-- System Details -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Application Info -->
      <div class="rounded-xl border border-white/[0.06] bg-card p-5">
        <h3 class="text-sm font-semibold text-foreground mb-4">Anwendung</h3>
        <div class="space-y-2.5">
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Version</span>
            <span class="font-mono text-xs text-foreground">{{ store.stats.system.version }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Framework</span>
            <span class="font-mono text-xs text-foreground">Django 5.1 + DRF</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Python</span>
            <span class="font-mono text-xs text-foreground">3.13</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Frontend</span>
            <span class="font-mono text-xs text-foreground">Vue 3 + Vite 7</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Betriebszeit</span>
            <span class="font-mono text-xs text-foreground">{{ store.stats.system.uptime }}</span>
          </div>
        </div>
      </div>

      <!-- Database Details -->
      <div class="rounded-xl border border-white/[0.06] bg-card p-5">
        <h3 class="text-sm font-semibold text-foreground mb-4">Datenbank</h3>
        <div class="space-y-2.5">
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Gesamtgröße</span>
            <span class="font-mono text-xs text-foreground">{{ store.stats.system.db_size }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Benutzer</span>
            <span class="font-mono text-xs text-foreground">{{ store.stats.users.total }} Zeilen</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Dokumente</span>
            <span class="font-mono text-xs text-foreground">{{ store.stats.documents.total }} Zeilen</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Host</span>
            <span class="font-mono text-xs text-foreground">gethub-postgres</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-500">Container</span>
            <span class="font-mono text-xs text-foreground">docker compose (shared)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Docker compose services -->
    <div class="rounded-xl border border-white/[0.06] bg-card p-5">
      <h3 class="text-sm font-semibold text-foreground mb-4">Docker-Dienste (docker-compose.prod.yml)</h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div v-for="service in ['web (Gunicorn)', 'nginx', 'redis', 'celery', 'beat']" :key="service" class="flex items-center gap-2 p-3 rounded-lg bg-zinc-900 border border-white/[0.04]">
          <div class="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
          <span class="font-mono text-xs text-foreground">{{ service }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
