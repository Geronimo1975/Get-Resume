<script setup lang="ts">
import type { AusbildungEntry, AusbildungContent } from '@/types'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import SectionEntryList from '@/components/editor/SectionEntryList.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getEntries(): AusbildungEntry[] {
  return ((props.content as unknown as AusbildungContent).eintraege ?? []) as AusbildungEntry[]
}

function updateEntry(index: number, field: keyof AusbildungEntry, value: unknown) {
  const entries = [...getEntries()]
  entries[index] = { ...entries[index], [field]: value } as AusbildungEntry
  emit('update', { ...props.content, eintraege: entries })
}

function addEntry() {
  const entries = [...getEntries()]
  entries.push({
    id: crypto.randomUUID(),
    abschluss: '',
    fachrichtung: '',
    institution: '',
    ort: '',
    von: '',
    bis: '',
    note: '',
    beschreibung: '',
  })
  emit('update', { ...props.content, eintraege: entries })
}

function removeEntry(index: number) {
  const entries = getEntries().filter((_, i) => i !== index)
  emit('update', { ...props.content, eintraege: entries })
}
</script>

<template>
  <SectionEntryList
    :entries="(getEntries() as unknown as Record<string, unknown>[])"
    add-label="Ausbildung hinzufugen"
    @add="addEntry"
    @remove="removeEntry"
  >
    <template #default="{ index }">
      <div class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.abschluss ?? ''" label="Abschluss" @update:model-value="updateEntry(index, 'abschluss', $event)" />
          <Input :model-value="getEntries()[index]?.fachrichtung ?? ''" label="Fachrichtung" @update:model-value="updateEntry(index, 'fachrichtung', $event)" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.institution ?? ''" label="Institution" @update:model-value="updateEntry(index, 'institution', $event)" />
          <Input :model-value="getEntries()[index]?.ort ?? ''" label="Ort" @update:model-value="updateEntry(index, 'ort', $event)" />
        </div>
        <div class="grid grid-cols-3 gap-3">
          <Input :model-value="getEntries()[index]?.von ?? ''" label="Von" type="month" @update:model-value="updateEntry(index, 'von', $event)" />
          <Input :model-value="getEntries()[index]?.bis ?? ''" label="Bis" type="month" @update:model-value="updateEntry(index, 'bis', $event)" />
          <Input :model-value="getEntries()[index]?.note ?? ''" label="Note" @update:model-value="updateEntry(index, 'note', $event)" />
        </div>
        <Textarea :model-value="getEntries()[index]?.beschreibung ?? ''" label="Beschreibung" rows="2" @update:model-value="updateEntry(index, 'beschreibung', $event)" />
      </div>
    </template>
  </SectionEntryList>
</template>
