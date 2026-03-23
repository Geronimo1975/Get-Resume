<script setup lang="ts">
import { computed } from 'vue'
import { useEditorStore } from '@/stores/editor'
import { SECTION_TYPES } from '@/lib/constants'
import type { SectionType } from '@/types'
import { GripVertical, Eye, EyeOff, Plus, Trash2 } from 'lucide-vue-next'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'
import Button from '@/components/ui/Button.vue'
import ScrollArea from '@/components/ui/ScrollArea.vue'

const editor = useEditorStore()

defineEmits<{
  addSection: [type: SectionType]
  removeSection: [id: string]
}>()

const availableSectionTypes = computed(() =>
  SECTION_TYPES.filter((t) => !editor.usedSectionTypes.has(t.value))
)

const sectionLabels = Object.fromEntries(SECTION_TYPES.map((t) => [t.value, t.label]))
</script>

<template>
  <div class="flex h-full flex-col border-r border-white/[0.06] bg-[#0d0d11]">
    <div class="flex items-center justify-between border-b border-white/[0.06] p-3">
      <h3 class="font-mono text-sm font-semibold text-foreground">Abschnitte</h3>
      <DropdownMenu v-if="availableSectionTypes.length > 0">
        <template #trigger>
          <Button variant="ghost" size="icon" class="h-7 w-7">
            <Plus class="h-4 w-4" />
          </Button>
        </template>
        <DropdownMenuItem
          v-for="type in availableSectionTypes"
          :key="type.value"
          @click="$emit('addSection', type.value)"
        >
          {{ type.label }}
        </DropdownMenuItem>
      </DropdownMenu>
    </div>

    <ScrollArea class="flex-1">
      <div class="space-y-0.5 p-2">
        <button
          v-for="section in editor.orderedSections"
          :key="section.id"
          :class="[
            'group flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors',
            section.id === editor.activeSectionId
              ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
              : 'text-zinc-500 hover:bg-white/[0.03] hover:text-foreground',
            !section.is_visible && 'opacity-50'
          ]"
          @click="editor.setActiveSection(section.id)"
        >
          <GripVertical class="h-3.5 w-3.5 shrink-0 cursor-grab text-muted-foreground/50" />
          <span class="flex-1 truncate text-left">
            {{ sectionLabels[section.section_type] || section.title }}
          </span>
          <button
            class="shrink-0 opacity-0 group-hover:opacity-100 hover:text-foreground transition-opacity"
            @click.stop="editor.toggleSectionVisibility(section.id)"
            :aria-label="section.is_visible ? 'Ausblenden' : 'Einblenden'"
          >
            <Eye v-if="section.is_visible" class="h-3.5 w-3.5" />
            <EyeOff v-else class="h-3.5 w-3.5" />
          </button>
          <button
            class="shrink-0 opacity-0 group-hover:opacity-100 hover:text-destructive transition-opacity"
            @click.stop="$emit('removeSection', section.id)"
            aria-label="Loschen"
          >
            <Trash2 class="h-3.5 w-3.5" />
          </button>
        </button>
      </div>
    </ScrollArea>
  </div>
</template>
