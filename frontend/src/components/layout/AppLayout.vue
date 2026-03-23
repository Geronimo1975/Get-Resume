<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, RouterLink, useRoute, useRouter } from 'vue-router'
import { LayoutDashboard, FileText, LayoutTemplate, Settings, CreditCard, ChevronLeft, ChevronRight, LogOut, ChevronsUpDown, Shield } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import Topbar from './Topbar.vue'
import SubscriptionBadge from './SubscriptionBadge.vue'
import MobileSidebar from './MobileSidebar.vue'
import Avatar from '@/components/ui/Avatar.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'
import Separator from '@/components/ui/Separator.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)

const navItems = computed(() => {
  const items = [
    { to: '/app', label: 'Ubersicht', icon: LayoutDashboard, exact: true },
    { to: '/app/documents', label: 'Meine Dokumente', icon: FileText },
    { to: '/app/templates', label: 'Vorlagen', icon: LayoutTemplate },
    { to: '/app/settings', label: 'Einstellungen', icon: Settings },
    { to: '/app/billing', label: 'Abonnement', icon: CreditCard },
  ]
  if (auth.isStaff) {
    items.push({ to: '/app/admin', label: 'Admin Zentrale', icon: Shield, exact: false } as any)
  }
  return items
})

function isActive(item: typeof navItems.value[number]) {
  if (item.exact) return route.path === item.to
  return route.path.startsWith(item.to)
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex h-screen bg-background">
    <!-- Desktop Sidebar -->
    <aside
      :class="[
        'hidden lg:flex flex-col border-r border-white/[0.06] bg-card transition-all duration-300 ease-in-out',
        sidebarCollapsed ? 'w-[68px]' : 'w-64'
      ]"
    >
      <!-- Logo -->
      <div class="flex h-16 items-center border-b border-white/[0.06] px-4">
        <RouterLink to="/app" class="flex items-center gap-2.5 min-w-0">
          <!-- Terminal-style >_ icon -->
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 font-mono text-indigo-400 text-xs font-bold shrink-0 select-none tracking-tighter">
            &gt;_
          </div>
          <span v-if="!sidebarCollapsed" class="text-base font-bold text-foreground whitespace-nowrap truncate">
            Get<span class="text-indigo-400">Resume</span>
          </span>
        </RouterLink>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 space-y-0.5 p-3 mt-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-mono transition-all duration-200 overflow-hidden',
            isActive(item)
              ? 'bg-indigo-500/10 text-indigo-400'
              : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.03]'
          ]"
        >
          <!-- Active indicator: left border bar with glow -->
          <div
            v-if="isActive(item)"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full bg-indigo-500 glow-sm"
          ></div>

          <component
            :is="item.icon"
            :class="[
              'h-4 w-4 shrink-0 transition-colors',
              isActive(item) ? 'text-indigo-400' : 'text-zinc-600 group-hover:text-zinc-400'
            ]"
          />
          <span v-if="!sidebarCollapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Sidebar footer: User menu -->
      <div class="border-t border-white/[0.06] p-3 space-y-2">
        <DropdownMenu>
          <template #trigger>
            <button
              :class="[
                'flex w-full items-center gap-3 rounded-lg p-2 text-left transition-colors hover:bg-white/[0.04]',
                sidebarCollapsed ? 'justify-center' : ''
              ]"
            >
              <Avatar :fallback="auth.userInitials" size="sm" />
              <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
                <p class="truncate text-sm font-medium text-foreground">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</p>
                <p class="truncate text-xs text-zinc-500 font-mono">{{ auth.user?.email }}</p>
              </div>
              <ChevronsUpDown v-if="!sidebarCollapsed" class="h-4 w-4 shrink-0 text-zinc-600" />
            </button>
          </template>

          <div class="px-3 py-2">
            <p class="text-sm font-medium text-foreground">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</p>
            <p class="text-xs text-zinc-500 font-mono">{{ auth.user?.email }}</p>
            <SubscriptionBadge class="mt-1.5" />
          </div>

          <Separator class="my-1" />

          <DropdownMenuItem @click="router.push('/app/settings')">
            <Settings class="mr-2 h-4 w-4" />
            Einstellungen
          </DropdownMenuItem>
          <DropdownMenuItem @click="router.push('/app/billing')">
            <CreditCard class="mr-2 h-4 w-4" />
            Abonnement
          </DropdownMenuItem>

          <Separator class="my-1" />

          <DropdownMenuItem destructive @click="handleLogout">
            <LogOut class="mr-2 h-4 w-4" />
            Abmelden
          </DropdownMenuItem>
        </DropdownMenu>

        <button
          class="flex w-full items-center justify-center rounded-lg p-1.5 text-zinc-600 hover:text-zinc-400 hover:bg-white/[0.03] transition-all duration-200"
          @click="toggleSidebar"
          :aria-label="sidebarCollapsed ? 'Sidebar ausklappen' : 'Sidebar einklappen'"
        >
          <ChevronLeft v-if="!sidebarCollapsed" class="h-3.5 w-3.5" />
          <ChevronRight v-else class="h-3.5 w-3.5" />
        </button>
      </div>
    </aside>

    <!-- Mobile Sidebar -->
    <MobileSidebar v-model:open="mobileSidebarOpen">
      <div class="flex h-full flex-col">
        <!-- Logo -->
        <div class="flex h-14 items-center mb-4">
          <RouterLink to="/app" class="flex items-center gap-2.5" @click="mobileSidebarOpen = false">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 font-mono text-indigo-400 text-xs font-bold shrink-0 select-none tracking-tighter">
              &gt;_
            </div>
            <span class="text-base font-bold text-foreground">Get<span class="text-indigo-400">Resume</span></span>
          </RouterLink>
        </div>

        <!-- Nav -->
        <nav class="flex-1 space-y-0.5">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            :class="[
              'group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-mono transition-all duration-200 overflow-hidden',
              isActive(item)
                ? 'bg-indigo-500/10 text-indigo-400'
                : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.03]'
            ]"
            @click="mobileSidebarOpen = false"
          >
            <div
              v-if="isActive(item)"
              class="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r-full bg-indigo-500 glow-sm"
            ></div>
            <component
              :is="item.icon"
              :class="[
                'h-4 w-4 shrink-0',
                isActive(item) ? 'text-indigo-400' : 'text-zinc-600 group-hover:text-zinc-400'
              ]"
            />
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>

        <!-- Mobile user footer -->
        <div class="border-t border-white/[0.06] pt-3 mt-3 space-y-2">
          <div class="flex items-center gap-3 rounded-lg p-2">
            <Avatar :fallback="auth.userInitials" size="sm" />
            <div class="flex-1 min-w-0">
              <p class="truncate text-sm font-medium text-foreground">{{ auth.user?.first_name }}</p>
              <p class="truncate text-xs text-zinc-500 font-mono">{{ auth.user?.email }}</p>
            </div>
            <SubscriptionBadge />
          </div>
          <button
            class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-mono text-red-400 hover:bg-red-500/10 transition-colors"
            @click="handleLogout"
          >
            <LogOut class="h-4 w-4" />
            Abmelden
          </button>
        </div>
      </div>
    </MobileSidebar>

    <!-- Main content area -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <Topbar
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="mobileSidebarOpen = !mobileSidebarOpen"
      />
      <main class="flex-1 overflow-y-auto">
        <div class="relative min-h-full">
          <div class="absolute inset-0 bg-dots opacity-20 pointer-events-none"></div>
          <div class="relative p-4 lg:p-8">
            <RouterView />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
