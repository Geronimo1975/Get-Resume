<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import { useEditorStore } from '@/stores/editor'
import { useAutosave } from '@/composables/useAutosave'
import { useSections } from '@/composables/useSections'
import { useToast } from '@/composables/useToast'
import { downloadPdf } from '@/api/documents'
import type { SectionType } from '@/types'
import EditorToolbar from '@/components/editor/EditorToolbar.vue'
import EditorLayout from '@/components/editor/EditorLayout.vue'
import ThemePicker from '@/components/editor/ThemePicker.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorDisplay from '@/components/shared/ErrorDisplay.vue'

const route = useRoute()
const router = useRouter()
const docs = useDocumentsStore()
const editor = useEditorStore()
const { toast } = useToast()
const { addSection, removeSection } = useSections()
useAutosave()

const loadError = ref(false)
const themeOpen = ref(false)

onMounted(async () => {
  const id = route.params.id as string
  try {
    const doc = await docs.fetchDocument(id)
    if (doc) editor.setDocument(doc)
  } catch {
    loadError.value = true
  }
})

function goBack() {
  router.push('/app/documents')
}

function handleAddSection(type: SectionType) {
  addSection(type)
}

function handleRemoveSection(id: string) {
  removeSection(id)
}

async function handleExportPdf() {
  if (!editor.document) return
  toast({ title: 'PDF-Export', description: 'PDF wird generiert...' })
  try {
    const blob = await downloadPdf(editor.document.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${editor.document.title || 'Lebenslauf'}.pdf`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Fertig', description: 'PDF wurde heruntergeladen.' })
  } catch {
    toast({ title: 'Fehler', description: 'PDF konnte nicht erstellt werden.', variant: 'destructive' })
  }
}
</script>

<template>
  <div class="flex h-screen flex-col bg-background">
    <!-- Loading -->
    <LoadingSpinner v-if="docs.loading" class="h-screen" size="lg" />

    <!-- Error -->
    <ErrorDisplay
      v-else-if="loadError"
      message="Dokument konnte nicht geladen werden."
      @retry="router.go(0)"
    />

    <!-- Editor -->
    <template v-else-if="editor.document">
      <EditorToolbar
        @back="goBack"
        @export-pdf="handleExportPdf"
        @open-theme="themeOpen = true"
      />
      <div class="flex-1 overflow-hidden">
        <EditorLayout
          @add-section="handleAddSection"
          @remove-section="handleRemoveSection"
        />
      </div>
    </template>

    <!-- Theme picker -->
    <ThemePicker v-model:open="themeOpen" />
  </div>
</template>
