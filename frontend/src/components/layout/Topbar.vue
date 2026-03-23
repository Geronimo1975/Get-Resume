<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'

defineProps<{
  sidebarCollapsed: boolean
}>()

defineEmits<{
  toggleSidebar: []
}>()

const route = useRoute()

const breadcrumb = computed(() => {
  const map: Record<string, string> = {
    '/app': 'Ubersicht',
    '/app/documents': 'Meine Dokumente',
    '/app/templates': 'Vorlagen',
    '/app/settings': 'Einstellungen',
    '/app/billing': 'Abonnement',
    '/app/admin': 'Admin Zentrale',
  }
  return map[route.path] || 'Dashboard'
})
</script>

<template>
  <header class="sticky top-0 z-40 flex h-12 items-center gap-4 border-b border-white/[0.06] glass px-4 lg:px-6">
    <button
      class="lg:hidden rounded-md p-2 text-zinc-500 hover:text-foreground hover:bg-white/5 transition-colors"
      @click="$emit('toggleSidebar')"
      aria-label="Menu"
    >
      <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 12h18M3 6h18M3 18h18" />
      </svg>
    </button>

    <div class="flex-1">
      <h2 class="font-mono text-sm text-zinc-500">{{ breadcrumb }}</h2>
    </div>
  </header>
</template>
