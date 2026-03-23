<script setup lang="ts">
import type { Document } from '@/types'
import DocumentCard from './DocumentCard.vue'

defineProps<{
  documents: Document[]
}>()

defineEmits<{
  edit: [doc: Document]
  duplicate: [doc: Document]
  download: [doc: Document]
  delete: [doc: Document]
}>()
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
    <DocumentCard
      v-for="doc in documents"
      :key="doc.id"
      :document="doc"
      @edit="$emit('edit', doc)"
      @duplicate="$emit('duplicate', doc)"
      @download="$emit('download', doc)"
      @delete="$emit('delete', doc)"
    />
  </div>
</template>
