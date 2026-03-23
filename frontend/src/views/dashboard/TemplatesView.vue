<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchTemplates } from '@/api/templates'
import { useDocumentsStore } from '@/stores/documents'
import { useToast } from '@/composables/useToast'
import type { Template } from '@/types'
import PageHeader from '@/components/shared/PageHeader.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import TemplateGrid from '@/components/templates/TemplateGrid.vue'
import TemplateFilter from '@/components/templates/TemplateFilter.vue'
import TemplatePreviewModal from '@/components/templates/TemplatePreviewModal.vue'

const router = useRouter()
const docs = useDocumentsStore()
const { toast } = useToast()

const templates = ref<Template[]>([])
const loading = ref(true)
const category = ref('alle')
const previewTemplate = ref<Template | null>(null)
const previewOpen = ref(false)

const filteredTemplates = computed(() => {
  if (category.value === 'alle') return templates.value
  return templates.value.filter((t) => t.category === category.value)
})

onMounted(async () => {
  try {
    const { data } = await fetchTemplates()
    templates.value = data.results
  } catch {
    toast({ title: 'Fehler', description: 'Vorlagen konnten nicht geladen werden.', variant: 'destructive' })
  } finally {
    loading.value = false
  }
})

function openPreview(tmpl: Template) {
  previewTemplate.value = tmpl
  previewOpen.value = true
}

async function applyTemplate() {
  if (!previewTemplate.value) return
  try {
    const doc = await docs.createDocument({
      title: `Neuer Lebenslauf - ${previewTemplate.value.name}`,
      doc_type: 'lebenslauf',
      template: previewTemplate.value.id,
    })
    previewOpen.value = false
    router.push(`/editor/${doc.id}`)
  } catch {
    toast({ title: 'Fehler', description: 'Dokument konnte nicht erstellt werden.', variant: 'destructive' })
  }
}
</script>

<template>
  <div>
    <PageHeader title="Vorlagen" description="Wahlen Sie eine professionelle Vorlage fur Ihren Lebenslauf" />

    <TemplateFilter v-model="category" class="mb-6" />

    <LoadingSpinner v-if="loading" class="py-12" />

    <EmptyState
      v-else-if="filteredTemplates.length === 0"
      title="Keine Vorlagen gefunden"
      description="Fur diese Kategorie sind noch keine Vorlagen verfugbar."
    />

    <TemplateGrid
      v-else
      :templates="filteredTemplates"
      @preview="openPreview"
      @apply="openPreview"
    />

    <TemplatePreviewModal
      v-model:open="previewOpen"
      :template="previewTemplate"
      @apply="applyTemplate"
    />
  </div>
</template>
