<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDocumentsStore } from '@/stores/documents'
import { useToast } from '@/composables/useToast'
import type { Document, DocType } from '@/types'
import { Plus } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import PageHeader from '@/components/shared/PageHeader.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'
import DocumentGrid from '@/components/documents/DocumentGrid.vue'
import DocumentList from '@/components/documents/DocumentList.vue'
import DocumentFilters from '@/components/documents/DocumentFilters.vue'
import CreateDocumentDialog from '@/components/documents/CreateDocumentDialog.vue'

const router = useRouter()
const route = useRoute()
const docs = useDocumentsStore()
const { toast } = useToast()

const viewMode = ref<'grid' | 'list'>('grid')
const createDialogOpen = ref(false)
const deleteDialogOpen = ref(false)
const documentToDelete = ref<Document | null>(null)

onMounted(() => {
  docs.fetchDocuments()
  if (route.query.create === 'true') {
    createDialogOpen.value = true
  }
})

async function handleCreate(payload: { title: string; doc_type: DocType }) {
  try {
    const doc = await docs.createDocument(payload)
    createDialogOpen.value = false
    router.push(`/editor/${doc.id}`)
  } catch {
    toast({ title: 'Fehler', description: 'Dokument konnte nicht erstellt werden.', variant: 'destructive' })
  }
}

function handleEdit(doc: Document) {
  router.push(`/editor/${doc.id}`)
}

async function handleDuplicate(doc: Document) {
  try {
    await docs.duplicateDocument(doc.id)
    toast({ title: 'Dupliziert', description: `"${doc.title}" wurde dupliziert.`, variant: 'success' })
  } catch {
    toast({ title: 'Fehler', description: 'Duplizieren fehlgeschlagen.', variant: 'destructive' })
  }
}

function handleDownload(_doc: Document) {
  toast({ title: 'PDF-Export', description: 'PDF wird generiert...' })
}

function confirmDelete(doc: Document) {
  documentToDelete.value = doc
  deleteDialogOpen.value = true
}

async function handleDelete() {
  if (!documentToDelete.value) return
  try {
    await docs.deleteDocument(documentToDelete.value.id)
    toast({ title: 'Geloscht', description: 'Dokument wurde geloscht.', variant: 'success' })
  } catch {
    toast({ title: 'Fehler', description: 'Loschen fehlgeschlagen.', variant: 'destructive' })
  }
  documentToDelete.value = null
}
</script>

<template>
  <div>
    <PageHeader title="Meine Dokumente" description="Erstellen und verwalten Sie Ihre Bewerbungsdokumente">
      <template #actions>
        <Button @click="createDialogOpen = true">
          <Plus class="h-4 w-4" />
          Neues Dokument
        </Button>
      </template>
    </PageHeader>

    <!-- Filters -->
    <DocumentFilters
      v-model:filter-type="docs.filterType"
      v-model:sort-by="docs.sortBy"
      v-model:view-mode="viewMode"
      :counts="docs.documentCounts"
      class="mb-6"
    />

    <!-- Loading -->
    <LoadingSpinner v-if="docs.loading" class="py-12" />

    <!-- Empty state -->
    <EmptyState
      v-else-if="docs.filteredDocuments.length === 0"
      title="Keine Dokumente gefunden"
      :description="docs.filterType === 'alle'
        ? 'Erstellen Sie Ihr erstes Dokument, um loszulegen.'
        : 'Keine Dokumente dieses Typs gefunden.'"
      action-label="Neues Dokument"
      @action="createDialogOpen = true"
    />

    <!-- Documents -->
    <template v-else>
      <DocumentGrid
        v-if="viewMode === 'grid'"
        :documents="docs.filteredDocuments"
        @edit="handleEdit"
        @duplicate="handleDuplicate"
        @download="handleDownload"
        @delete="confirmDelete"
      />
      <DocumentList
        v-else
        :documents="docs.filteredDocuments"
        @edit="handleEdit"
        @duplicate="handleDuplicate"
        @download="handleDownload"
        @delete="confirmDelete"
      />
    </template>

    <!-- Create dialog -->
    <CreateDocumentDialog
      v-model:open="createDialogOpen"
      @create="handleCreate"
    />

    <!-- Delete confirmation -->
    <ConfirmDialog
      v-model:open="deleteDialogOpen"
      title="Dokument loschen?"
      :description="`Mochten Sie '${documentToDelete?.title}' wirklich loschen? Diese Aktion kann nicht ruckgangig gemacht werden.`"
      confirm-label="Loschen"
      destructive
      @confirm="handleDelete"
    />
  </div>
</template>
