<script setup lang="ts">
import { useEditorStore } from '@/stores/editor'
import { Check, Loader2, AlertCircle } from 'lucide-vue-next'

const editor = useEditorStore()
</script>

<template>
  <div class="flex items-center gap-1.5 text-xs">
    <template v-if="editor.saving">
      <Loader2 class="h-3.5 w-3.5 animate-spin text-muted-foreground" />
      <span class="text-muted-foreground">Speichere...</span>
    </template>
    <template v-else-if="editor.saveError">
      <AlertCircle class="h-3.5 w-3.5 text-destructive" />
      <span class="text-destructive">Fehler beim Speichern</span>
    </template>
    <template v-else-if="editor.dirty">
      <span class="text-muted-foreground">Ungespeichert</span>
    </template>
    <template v-else>
      <Check class="h-3.5 w-3.5 text-emerald-500" />
      <span class="text-emerald-600">Gespeichert</span>
    </template>
  </div>
</template>
