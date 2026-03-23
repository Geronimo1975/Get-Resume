<script setup lang="ts">
import type { WeiterbildungEntry, WeiterbildungenContent } from '@/types'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import SectionEntryList from '@/components/editor/SectionEntryList.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getEntries(): WeiterbildungEntry[] {
  return ((props.content as unknown as WeiterbildungenContent).eintraege ?? []) as WeiterbildungEntry[]
}

function updateEntry(index: number, field: keyof WeiterbildungEntry, value: unknown) {
  const entries = [...getEntries()]
  entries[index] = { ...entries[index], [field]: value } as WeiterbildungEntry
  emit('update', { ...props.content, eintraege: entries })
}

function addEntry() {
  const entries = [...getEntries()]
  entries.push({ id: crypto.randomUUID(), titel: '', anbieter: '', datum: '', beschreibung: '' })
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
    add-label="Weiterbildung hinzufugen"
    @add="addEntry"
    @remove="removeEntry"
  >
    <template #default="{ index }">
      <div class="space-y-3">
        <Input :model-value="getEntries()[index]?.titel ?? ''" label="Titel" @update:model-value="updateEntry(index, 'titel', $event)" />
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.anbieter ?? ''" label="Anbieter" @update:model-value="updateEntry(index, 'anbieter', $event)" />
          <Input :model-value="getEntries()[index]?.datum ?? ''" label="Datum" type="date" @update:model-value="updateEntry(index, 'datum', $event)" />
        </div>
        <Textarea :model-value="getEntries()[index]?.beschreibung ?? ''" label="Beschreibung" rows="2" @update:model-value="updateEntry(index, 'beschreibung', $event)" />
      </div>
    </template>
  </SectionEntryList>
</template>
