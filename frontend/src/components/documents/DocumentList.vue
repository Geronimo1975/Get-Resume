<script setup lang="ts">
import type { Document } from '@/types'
import { formatRelativeDE } from '@/lib/formatters'
import { FileText, MoreVertical, Pencil, Copy, Download, Trash2 } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'

defineProps<{
  documents: Document[]
}>()

defineEmits<{
  edit: [doc: Document]
  duplicate: [doc: Document]
  download: [doc: Document]
  delete: [doc: Document]
}>()

const typeLabels: Record<string, string> = {
  lebenslauf: 'Lebenslauf',
  anschreiben: 'Anschreiben',
  deckblatt: 'Deckblatt',
}
</script>

<template>
  <div class="divide-y divide-border rounded-lg border border-border bg-card">
    <div
      v-for="doc in documents"
      :key="doc.id"
      class="flex items-center gap-4 p-4 hover:bg-accent/50 transition-colors"
    >
      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
        <FileText class="h-5 w-5 text-muted-foreground" />
      </div>

      <div class="min-w-0 flex-1 cursor-pointer" @click="$emit('edit', doc)">
        <p class="truncate font-medium text-foreground">{{ doc.title }}</p>
        <p class="text-xs text-muted-foreground">{{ formatRelativeDE(doc.updated_at) }}</p>
      </div>

      <Badge variant="secondary" class="hidden sm:inline-flex">
        {{ typeLabels[doc.doc_type] || doc.doc_type }}
      </Badge>

      <DropdownMenu>
        <template #trigger>
          <button class="rounded-md p-1 hover:bg-accent transition-colors">
            <MoreVertical class="h-4 w-4 text-muted-foreground" />
          </button>
        </template>
        <DropdownMenuItem @click="$emit('edit', doc)">
          <Pencil class="h-4 w-4" /> Bearbeiten
        </DropdownMenuItem>
        <DropdownMenuItem @click="$emit('duplicate', doc)">
          <Copy class="h-4 w-4" /> Duplizieren
        </DropdownMenuItem>
        <DropdownMenuItem @click="$emit('download', doc)">
          <Download class="h-4 w-4" /> PDF herunterladen
        </DropdownMenuItem>
        <DropdownMenuItem destructive @click="$emit('delete', doc)">
          <Trash2 class="h-4 w-4" /> Loschen
        </DropdownMenuItem>
      </DropdownMenu>
    </div>
  </div>
</template>
