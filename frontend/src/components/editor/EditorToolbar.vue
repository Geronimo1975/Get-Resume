<script setup lang="ts">
import { useEditorStore } from '@/stores/editor'
import { ArrowLeft, Palette, Download } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import AutosaveIndicator from './AutosaveIndicator.vue'

const editor = useEditorStore()

defineEmits<{
  back: []
  exportPdf: []
  openTheme: []
}>()
</script>

<template>
  <header class="flex h-14 items-center gap-3 border-b border-white/[0.06] glass px-4">
    <Button variant="ghost" size="icon" @click="$emit('back')" aria-label="Zuruck">
      <ArrowLeft class="h-5 w-5" />
    </Button>

    <!-- Editable title -->
    <input
      v-if="editor.document"
      v-model="editor.document.title"
      class="flex-1 bg-transparent font-mono text-lg font-semibold text-foreground outline-none focus:ring-0 border-none"
      @input="editor.dirty = true"
    />

    <AutosaveIndicator />

    <div class="flex items-center gap-1">
      <Button variant="ghost" size="icon" @click="$emit('openTheme')" aria-label="Design">
        <Palette class="h-5 w-5" />
      </Button>
      <Button variant="outline" size="sm" @click="$emit('exportPdf')">
        <Download class="h-4 w-4" />
        PDF
      </Button>
    </div>
  </header>
</template>
