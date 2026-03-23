<script setup lang="ts">
import type { DocType } from '@/types'
import { LayoutGrid, List } from 'lucide-vue-next'
import Tabs from '@/components/ui/Tabs.vue'
import Select from '@/components/ui/Select.vue'

const props = defineProps<{
  filterType: DocType | 'alle'
  sortBy: string
  viewMode: 'grid' | 'list'
  counts: Record<string, number>
}>()

const emit = defineEmits<{
  'update:filterType': [value: DocType | 'alle']
  'update:sortBy': [value: string]
  'update:viewMode': [value: 'grid' | 'list']
}>()

const tabs = [
  { value: 'alle', label: 'Alle', count: props.counts.alle },
  { value: 'lebenslauf', label: 'Lebenslauf', count: props.counts.lebenslauf },
  { value: 'anschreiben', label: 'Anschreiben', count: props.counts.anschreiben },
  { value: 'deckblatt', label: 'Deckblatt', count: props.counts.deckblatt },
]

const sortOptions = [
  { value: 'updated_at', label: 'Zuletzt bearbeitet' },
  { value: 'created_at', label: 'Erstellt am' },
  { value: 'title', label: 'Name (A-Z)' },
]
</script>

<template>
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
    <Tabs
      :model-value="filterType"
      :tabs="tabs"
      @update:model-value="emit('update:filterType', $event as DocType | 'alle')"
    />

    <div class="flex items-center gap-2">
      <Select
        :model-value="sortBy"
        :options="sortOptions"
        class="w-48"
        @update:model-value="emit('update:sortBy', $event)"
      />
      <div class="flex rounded-lg border border-border bg-muted p-0.5">
        <button
          :class="['rounded-md p-1.5 transition-colors', viewMode === 'grid' ? 'bg-background shadow-sm' : 'text-muted-foreground']"
          @click="emit('update:viewMode', 'grid')"
          aria-label="Rasteransicht"
        >
          <LayoutGrid class="h-4 w-4" />
        </button>
        <button
          :class="['rounded-md p-1.5 transition-colors', viewMode === 'list' ? 'bg-background shadow-sm' : 'text-muted-foreground']"
          @click="emit('update:viewMode', 'list')"
          aria-label="Listenansicht"
        >
          <List class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>
