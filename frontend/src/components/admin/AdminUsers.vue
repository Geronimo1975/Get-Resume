<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { formatDateShortDE, formatRelativeDE } from '@/lib/formatters'
import {
  Search, Users, Shield, ShieldOff, UserX, ChevronLeft, ChevronRight, MoreHorizontal,
} from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import Table from '@/components/ui/Table.vue'
import Select from '@/components/ui/Select.vue'
import Skeleton from '@/components/ui/Skeleton.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'
import UserDetailSheet from './UserDetailSheet.vue'

const store = useAdminStore()

let searchTimeout: ReturnType<typeof setTimeout>

function onSearch(e: Event) {
  const val = (e.target as HTMLInputElement).value
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    store.userFilters.search = val
    store.userFilters.page = 1
    store.loadUsers()
  }, 400)
}

function onFilterChange() {
  store.userFilters.page = 1
  store.loadUsers()
}

function prevPage() {
  if (store.userFilters.page > 1) {
    store.userFilters.page--
    store.loadUsers()
  }
}

function nextPage() {
  if (store.userFilters.page < store.totalPages.users) {
    store.userFilters.page++
    store.loadUsers()
  }
}

function openUserDetail(id: string) {
  store.loadUser(id)
}

function closeDetail() {
  store.selectedUser = null
}

async function handleToggleActive(id: string) {
  await store.toggleActive(id)
}

async function handleToggleStaff(id: string) {
  await store.toggleStaff(id)
}

async function handleDeactivate(id: string) {
  if (confirm('Benutzer wirklich deaktivieren?')) {
    await store.deactivateUser(id)
  }
}

function planBadgeClass(plan: string) {
  switch (plan) {
    case 'premium_monthly':
    case 'premium_yearly':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'business':
      return 'bg-violet-500/10 text-violet-400 border-violet-500/20'
    default:
      return 'bg-zinc-800 text-zinc-400 border-zinc-700'
  }
}

function planLabel(plan: string) {
  const labels: Record<string, string> = {
    free: 'Free',
    premium_monthly: 'Premium M',
    premium_yearly: 'Premium J',
    business: 'Business',
  }
  return labels[plan] || plan
}

onMounted(() => {
  store.loadUsers()
})
</script>

<template>
  <div class="space-y-4">
    <!-- Search & Filters -->
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
        <Input
          type="text"
          placeholder="Suche nach E-Mail oder Name..."
          class="pl-10"
          @input="onSearch"
        />
      </div>
      <div class="flex gap-2">
        <select
          v-model="store.userFilters.is_active"
          class="rounded-lg border border-white/[0.08] bg-zinc-900 px-3 py-2 text-sm text-foreground"
          @change="onFilterChange"
        >
          <option value="">Alle Status</option>
          <option value="true">Aktiv</option>
          <option value="false">Inaktiv</option>
        </select>
        <select
          v-model="store.userFilters.is_staff"
          class="rounded-lg border border-white/[0.08] bg-zinc-900 px-3 py-2 text-sm text-foreground"
          @change="onFilterChange"
        >
          <option value="">Alle Rollen</option>
          <option value="true">Staff</option>
          <option value="false">Benutzer</option>
        </select>
        <select
          v-model="store.userFilters.subscription_plan"
          class="rounded-lg border border-white/[0.08] bg-zinc-900 px-3 py-2 text-sm text-foreground"
          @change="onFilterChange"
        >
          <option value="">Alle Tarife</option>
          <option value="free">Kostenlos</option>
          <option value="premium_monthly">Premium Monatlich</option>
          <option value="premium_yearly">Premium Jährlich</option>
          <option value="business">Business</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="rounded-xl border border-white/[0.06] bg-card overflow-hidden">
      <div v-if="store.loading.users" class="p-8 space-y-3">
        <Skeleton v-for="i in 5" :key="i" class="h-12 w-full rounded-lg" />
      </div>

      <Table v-else>
        <thead>
          <tr>
            <th>Benutzer</th>
            <th>E-Mail</th>
            <th>Tarif</th>
            <th>Dokumente</th>
            <th>Status</th>
            <th>Registriert</th>
            <th>Letzter Login</th>
            <th class="text-right">Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.users.length === 0">
            <td colspan="8" class="text-center py-12">
              <Users class="h-8 w-8 text-zinc-700 mx-auto mb-3" />
              <p class="text-sm text-zinc-500">Keine Benutzer gefunden</p>
            </td>
          </tr>
          <tr
            v-for="user in store.users"
            :key="user.id"
            class="hover:bg-white/[0.02] cursor-pointer transition-colors"
            @click="openUserDetail(user.id)"
          >
            <td>
              <div class="flex items-center gap-3">
                <div class="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700 text-xs font-mono font-bold text-zinc-400 shrink-0">
                  {{ (user.first_name?.[0] || '') + (user.last_name?.[0] || '') || '?' }}
                </div>
                <span class="font-medium">{{ user.first_name }} {{ user.last_name }}</span>
              </div>
            </td>
            <td class="font-mono text-xs text-zinc-400">{{ user.email }}</td>
            <td>
              <Badge :class="['text-[10px] font-mono border', planBadgeClass(user.subscription_plan)]">
                {{ planLabel(user.subscription_plan) }}
              </Badge>
            </td>
            <td class="font-mono text-sm">{{ user.document_count }}</td>
            <td>
              <div class="flex items-center gap-1.5">
                <div :class="['h-1.5 w-1.5 rounded-full', user.is_active ? 'bg-emerald-500' : 'bg-red-500']"></div>
                <span :class="['text-xs', user.is_active ? 'text-emerald-400' : 'text-red-400']">
                  {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
                </span>
                <Badge v-if="user.is_staff" class="ml-1 bg-violet-500/10 text-violet-400 border-violet-500/20 text-[9px] font-mono">
                  Staff
                </Badge>
              </div>
            </td>
            <td class="font-mono text-xs text-zinc-500">{{ formatDateShortDE(user.date_joined) }}</td>
            <td class="font-mono text-xs text-zinc-500">
              {{ user.last_login ? formatRelativeDE(user.last_login) : '—' }}
            </td>
            <td class="text-right" @click.stop>
              <DropdownMenu>
                <template #trigger>
                  <button class="p-1.5 rounded-lg hover:bg-white/5 transition-colors">
                    <MoreHorizontal class="h-4 w-4 text-zinc-500" />
                  </button>
                </template>
                <DropdownMenuItem @click="handleToggleActive(user.id)">
                  <UserX class="h-4 w-4" />
                  {{ user.is_active ? 'Deaktivieren' : 'Aktivieren' }}
                </DropdownMenuItem>
                <DropdownMenuItem @click="handleToggleStaff(user.id)">
                  <component :is="user.is_staff ? ShieldOff : Shield" class="h-4 w-4" />
                  {{ user.is_staff ? 'Staff entfernen' : 'Staff erteilen' }}
                </DropdownMenuItem>
                <DropdownMenuItem v-if="user.is_active" destructive @click="handleDeactivate(user.id)">
                  <UserX class="h-4 w-4" />
                  Benutzer deaktivieren
                </DropdownMenuItem>
              </DropdownMenu>
            </td>
          </tr>
        </tbody>
      </Table>

      <!-- Pagination -->
      <div v-if="store.userCount > 0" class="flex items-center justify-between px-5 py-3 border-t border-white/[0.04]">
        <span class="text-xs font-mono text-zinc-500">
          {{ store.userCount }} Benutzer — Seite {{ store.userFilters.page }} von {{ store.totalPages.users }}
        </span>
        <div class="flex gap-1">
          <button
            class="p-1.5 rounded-lg border border-white/[0.06] hover:bg-white/5 disabled:opacity-30 transition-colors"
            :disabled="store.userFilters.page <= 1"
            @click="prevPage"
          >
            <ChevronLeft class="h-4 w-4" />
          </button>
          <button
            class="p-1.5 rounded-lg border border-white/[0.06] hover:bg-white/5 disabled:opacity-30 transition-colors"
            :disabled="store.userFilters.page >= store.totalPages.users"
            @click="nextPage"
          >
            <ChevronRight class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- User Detail Sheet -->
    <UserDetailSheet
      :open="!!store.selectedUser"
      :user="store.selectedUser"
      @close="closeDetail"
      @toggle-active="handleToggleActive"
      @toggle-staff="handleToggleStaff"
    />
  </div>
</template>
