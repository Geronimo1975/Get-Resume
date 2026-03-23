<script setup lang="ts">
import { useEditorStore } from '@/stores/editor'
import Dialog from '@/components/ui/Dialog.vue'

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const editor = useEditorStore()

const themes = [
  { id: 'blue', label: 'Blau', color: '#2563eb' },
  { id: 'gray', label: 'Grau', color: '#4b5563' },
  { id: 'green', label: 'Grun', color: '#059669' },
  { id: 'red', label: 'Rot', color: '#dc2626' },
  { id: 'purple', label: 'Lila', color: '#7c3aed' },
  { id: 'orange', label: 'Orange', color: '#ea580c' },
  { id: 'teal', label: 'Petrol', color: '#0d9488' },
  { id: 'slate', label: 'Schiefer', color: '#475569' },
]

function selectTheme(themeId: string) {
  if (!editor.document) return
  editor.document.theme = themeId
  editor.dirty = true
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <h2 class="text-lg font-semibold text-foreground mb-4">Farbschema wahlen</h2>
    <div class="grid grid-cols-4 gap-3">
      <button
        v-for="theme in themes"
        :key="theme.id"
        :class="[
          'flex flex-col items-center gap-2 rounded-lg p-3 border-2 transition-colors',
          editor.document?.theme === theme.id ? 'border-primary-600' : 'border-border hover:border-primary-300'
        ]"
        @click="selectTheme(theme.id)"
      >
        <div
          class="h-8 w-8 rounded-full"
          :style="{ backgroundColor: theme.color }"
        />
        <span class="text-xs text-foreground">{{ theme.label }}</span>
      </button>
    </div>
  </Dialog>
</template>
