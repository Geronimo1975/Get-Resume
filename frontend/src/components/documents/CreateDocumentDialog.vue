<script setup lang="ts">
import { ref } from 'vue'
import type { DocType } from '@/types'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import Button from '@/components/ui/Button.vue'

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  create: [payload: { title: string; doc_type: DocType }]
}>()

const title = ref('Neuer Lebenslauf')
const docType = ref<DocType>('lebenslauf')
const loading = ref(false)

const docTypeOptions = [
  { value: 'lebenslauf', label: 'Lebenslauf' },
  { value: 'anschreiben', label: 'Anschreiben' },
  { value: 'deckblatt', label: 'Deckblatt' },
]

function handleCreate() {
  loading.value = true
  emit('create', { title: title.value, doc_type: docType.value })
}

function resetAndClose() {
  title.value = 'Neuer Lebenslauf'
  docType.value = 'lebenslauf'
  loading.value = false
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="resetAndClose">
    <h2 class="text-lg font-semibold text-foreground mb-4">Neues Dokument erstellen</h2>

    <form class="space-y-4" @submit.prevent="handleCreate">
      <Input
        v-model="title"
        label="Titel"
        placeholder="z.B. Lebenslauf Softwareentwickler"
        required
      />

      <Select
        v-model="docType"
        label="Dokumenttyp"
        :options="docTypeOptions"
      />

      <div class="flex justify-end gap-3 pt-2">
        <Button variant="outline" type="button" @click="resetAndClose">
          Abbrechen
        </Button>
        <Button type="submit" :loading="loading">
          Erstellen
        </Button>
      </div>
    </form>
  </Dialog>
</template>
