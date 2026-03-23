<script setup lang="ts">
import { onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { formatDateShortDE } from '@/lib/formatters'
import {
  Search, FileText, RotateCcw, Trash2, ChevronLeft, ChevronRight, MoreHorizontal,
} from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import Table from '@/components/ui/Table.vue'
import Skeleton from '@/components/ui/Skeleton.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'

const store = useAdminStore()

let searchTimeout: ReturnType<typeof setTimeout>

function onSearch(e: Event) {
  const val = (e.target as HTMLInputElement).value
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    store.docFilters.search = val
    store.docFilters.page = 1
    store.loadDocuments()
  }, 400)
}

function onFilterChange() {
  store.docFilters.page = 1
  store.loadDocuments()
}

function prevPage() {
  if (store.docFilters.page > 1) {
    store.docFilters.page--
    store.loadDocuments()
  }
}

function nextPage() {
  if (store.docFilters.page < store.totalPages.documents) {
    store.docFilters.page++
    store.loadDocuments()
  }
}

async function handleRestore(id: string) {
  await store.restoreDoc(id)
}

async function handleHardDelete(id: string) {
  if (confirm('Dokument endgültig löschen? Dies kann nicht rückgängig gemacht werden.')) {
    await store.hardDeleteDoc(id)
  }
}

function docTypeBadge(type: string) {
  switch (type) {
    case 'lebenslauf': return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
    case 'anschreiben': return 'bg-violet-500/10 text-violet-400 border-violet-500/20'
    case 'deckblatt': return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    default: return 'bg-zinc-800 text-zinc-400 border-zinc-700'
  }
}

function docTypeLabel(type: string) {
  const labels: Record<string, string> = {
    lebenslauf: 'Lebenslauf',
    anschreiben: 'Anschreiben',
    deckblatt: 'Deckblatt',
  }
  return labels[type] || type
}

onMounted(() => {
  store.loadDocuments()
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
          placeholder="Suche nach Titel oder E-Mail..."
          class="pl-10"
          @input="onSearch"
        />
      </div>
      <div class="flex gap-2">
        <select
          v-model="store.docFilters.doc_type"
          class="rounded-lg border border-white/[0.08] bg-zinc-900 px-3 py-2 text-sm text-foreground"
          @change="onFilterChange"
        >
          <option value="">Alle Typen</option>
          <option value="lebenslauf">Lebenslauf</option>
          <option value="anschreiben">Anschreiben</option>
          <option value="deckblatt">Deckblatt</option>
        </select>
        <select
          v-model="store.docFilters.is_deleted"
          class="rounded-lg border border-white/[0.08] bg-zinc-900 px-3 py-2 text-sm text-foreground"
          @change="onFilterChange"
        >
          <option value="">Alle</option>
          <option value="false">Aktiv</option>
          <option value="true">Gelöscht</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="rounded-xl border border-white/[0.06] bg-card overflow-hidden">
      <div v-if="store.loading.documents" class="p-8 space-y-3">
        <Skeleton v-for="i in 5" :key="i" class="h-12 w-full rounded-lg" />
      </div>

      <Table v-else>
        <thead>
          <tr>
            <th>Titel</th>
            <th>Typ</th>
            <th>Benutzer</th>
            <th>Vorlage</th>
            <th>Abschnitte</th>
            <th>Erstellt</th>
            <th>Status</th>
            <th class="text-right">Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="store.documents.length === 0">
            <td colspan="8" class="text-center py-12">
              <FileText class="h-8 w-8 text-zinc-700 mx-auto mb-3" />
              <p class="text-sm text-zinc-500">Keine Dokumente gefunden</p>
            </td>
          </tr>
          <tr
            v-for="doc in store.documents"
            :key="doc.id"
            class="hover:bg-white/[0.02] transition-colors"
          >
            <td>
              <span class="font-medium">{{ doc.title }}</span>
            </td>
            <td>
              <Badge :class="['text-[10px] font-mono border', docTypeBadge(doc.doc_type)]">
                {{ docTypeLabel(doc.doc_type) }}
              </Badge>
            </td>
            <td class="font-mono text-xs text-zinc-400">{{ doc.user_email }}</td>
            <td class="text-xs text-zinc-500">{{ doc.template_name || '—' }}</td>
            <td class="font-mono text-sm text-center">{{ doc.section_count }}</td>
            <td class="font-mono text-xs text-zinc-500">{{ formatDateShortDE(doc.created_at) }}</td>
            <td>
              <div class="flex items-center gap-1.5">
                <div :class="['h-1.5 w-1.5 rounded-full', doc.deleted_at ? 'bg-red-500' : 'bg-emerald-500']"></div>
                <span :class="['text-xs', doc.deleted_at ? 'text-red-400' : 'text-emerald-400']">
                  {{ doc.deleted_at ? 'Gelöscht' : 'Aktiv' }}
                </span>
                <Badge v-if="doc.is_premium" class="ml-1 bg-amber-500/10 text-amber-400 border-amber-500/20 text-[9px] font-mono">
                  Premium
                </Badge>
              </div>
            </td>
            <td class="text-right">
              <DropdownMenu>
                <template #trigger>
                  <button class="p-1.5 rounded-lg hover:bg-white/5 transition-colors">
                    <MoreHorizontal class="h-4 w-4 text-zinc-500" />
                  </button>
                </template>
                <DropdownMenuItem v-if="doc.deleted_at" @click="handleRestore(doc.id)">
                  <RotateCcw class="h-4 w-4" />
                  Wiederherstellen
                </DropdownMenuItem>
                <DropdownMenuItem destructive @click="handleHardDelete(doc.id)">
                  <Trash2 class="h-4 w-4" />
                  Endgültig löschen
                </DropdownMenuItem>
              </DropdownMenu>
            </td>
          </tr>
        </tbody>
      </Table>

      <!-- Pagination -->
      <div v-if="store.documentCount > 0" class="flex items-center justify-between px-5 py-3 border-t border-white/[0.04]">
        <span class="text-xs font-mono text-zinc-500">
          {{ store.documentCount }} Dokumente — Seite {{ store.docFilters.page }} von {{ store.totalPages.documents }}
        </span>
        <div class="flex gap-1">
          <button
            class="p-1.5 rounded-lg border border-white/[0.06] hover:bg-white/5 disabled:opacity-30 transition-colors"
            :disabled="store.docFilters.page <= 1"
            @click="prevPage"
          >
            <ChevronLeft class="h-4 w-4" />
          </button>
          <button
            class="p-1.5 rounded-lg border border-white/[0.06] hover:bg-white/5 disabled:opacity-30 transition-colors"
            :disabled="store.docFilters.page >= store.totalPages.documents"
            @click="nextPage"
          >
            <ChevronRight class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
