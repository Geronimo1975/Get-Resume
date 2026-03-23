<script setup lang="ts">
import type { Document } from '@/types'
import { formatRelativeDE } from '@/lib/formatters'
import { FileText, MoreVertical, Pencil, Copy, Download, Trash2 } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'

defineProps<{
  document: Document
}>()

defineEmits<{
  edit: []
  duplicate: []
  download: []
  delete: []
}>()

const typeLabels: Record<string, string> = {
  lebenslauf: 'Lebenslauf',
  anschreiben: 'Anschreiben',
  deckblatt: 'Deckblatt',
}
</script>

<template>
  <div class="group relative rounded-lg border border-border bg-card p-4 transition-shadow hover:shadow-md">
    <!-- Thumbnail area -->
    <div
      class="mb-3 flex h-32 items-center justify-center rounded-md bg-muted cursor-pointer"
      @click="$emit('edit')"
    >
      <FileText class="h-12 w-12 text-muted-foreground/50" />
    </div>

    <!-- Content -->
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0 flex-1 cursor-pointer" @click="$emit('edit')">
        <p class="truncate font-medium text-foreground">{{ document.title }}</p>
        <p class="mt-0.5 text-xs text-muted-foreground">
          {{ formatRelativeDE(document.updated_at) }}
        </p>
      </div>

      <DropdownMenu>
        <template #trigger>
          <button class="rounded-md p-1 opacity-0 group-hover:opacity-100 hover:bg-accent transition-all">
            <MoreVertical class="h-4 w-4 text-muted-foreground" />
          </button>
        </template>
        <DropdownMenuItem @click="$emit('edit')">
          <Pencil class="h-4 w-4" /> Bearbeiten
        </DropdownMenuItem>
        <DropdownMenuItem @click="$emit('duplicate')">
          <Copy class="h-4 w-4" /> Duplizieren
        </DropdownMenuItem>
        <DropdownMenuItem @click="$emit('download')">
          <Download class="h-4 w-4" /> PDF herunterladen
        </DropdownMenuItem>
        <DropdownMenuItem destructive @click="$emit('delete')">
          <Trash2 class="h-4 w-4" /> Loschen
        </DropdownMenuItem>
      </DropdownMenu>
    </div>

    <!-- Type badge -->
    <Badge variant="secondary" class="mt-2">
      {{ typeLabels[document.doc_type] || document.doc_type }}
    </Badge>

    <!-- Premium indicator -->
    <Badge v-if="document.is_premium" variant="premium" class="absolute top-2 right-2">
      Premium
    </Badge>
  </div>
</template>
