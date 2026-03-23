<script setup lang="ts">
import type { BerufserfahrungEntry, BerufserfahrungContent } from '@/types'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import SectionEntryList from '@/components/editor/SectionEntryList.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getEntries(): BerufserfahrungEntry[] {
  return ((props.content as unknown as BerufserfahrungContent).eintraege ?? []) as BerufserfahrungEntry[]
}

function updateEntry(index: number, field: keyof BerufserfahrungEntry, value: unknown) {
  const entries = [...getEntries()]
  entries[index] = { ...entries[index], [field]: value } as BerufserfahrungEntry
  emit('update', { ...props.content, eintraege: entries })
}

function addEntry() {
  const entries = [...getEntries()]
  entries.push({
    id: crypto.randomUUID(),
    position: '',
    unternehmen: '',
    ort: '',
    von: '',
    bis: '',
    ist_aktuell: false,
    beschreibung: '',
    aufgaben: [],
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
    add-label="Berufserfahrung hinzufugen"
    @add="addEntry"
    @remove="removeEntry"
  >
    <template #default="{ index }">
      <div class="space-y-3">
        <Input :model-value="getEntries()[index]?.position ?? ''" label="Position" @update:model-value="updateEntry(index, 'position', $event)" />
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.unternehmen ?? ''" label="Unternehmen" @update:model-value="updateEntry(index, 'unternehmen', $event)" />
          <Input :model-value="getEntries()[index]?.ort ?? ''" label="Ort" @update:model-value="updateEntry(index, 'ort', $event)" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.von ?? ''" label="Von" type="month" @update:model-value="updateEntry(index, 'von', $event)" />
          <Input :model-value="getEntries()[index]?.bis ?? ''" label="Bis" type="month" :disabled="getEntries()[index]?.ist_aktuell" @update:model-value="updateEntry(index, 'bis', $event)" />
        </div>
        <Checkbox :model-value="getEntries()[index]?.ist_aktuell ?? false" label="Bis heute" @update:model-value="updateEntry(index, 'ist_aktuell', $event)" />
        <Textarea :model-value="getEntries()[index]?.beschreibung ?? ''" label="Beschreibung" rows="3" @update:model-value="updateEntry(index, 'beschreibung', $event)" />
      </div>
    </template>
  </SectionEntryList>
</template>
