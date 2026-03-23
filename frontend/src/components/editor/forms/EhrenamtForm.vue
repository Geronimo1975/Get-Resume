<script setup lang="ts">
import type { EhrenamtEntry, EhrenamtContent } from '@/types'
import Input from '@/components/ui/Input.vue'
import Textarea from '@/components/ui/Textarea.vue'
import SectionEntryList from '@/components/editor/SectionEntryList.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getEntries(): EhrenamtEntry[] {
  return ((props.content as unknown as EhrenamtContent).eintraege ?? []) as EhrenamtEntry[]
}

function updateEntry(index: number, field: keyof EhrenamtEntry, value: unknown) {
  const entries = [...getEntries()]
  entries[index] = { ...entries[index], [field]: value } as EhrenamtEntry
  emit('update', { ...props.content, eintraege: entries })
}

function addEntry() {
  const entries = [...getEntries()]
  entries.push({ id: crypto.randomUUID(), rolle: '', organisation: '', von: '', bis: '', beschreibung: '' })
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
    add-label="Ehrenamt hinzufugen"
    @add="addEntry"
    @remove="removeEntry"
  >
    <template #default="{ index }">
      <div class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.rolle ?? ''" label="Rolle" @update:model-value="updateEntry(index, 'rolle', $event)" />
          <Input :model-value="getEntries()[index]?.organisation ?? ''" label="Organisation" @update:model-value="updateEntry(index, 'organisation', $event)" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.von ?? ''" label="Von" type="month" @update:model-value="updateEntry(index, 'von', $event)" />
          <Input :model-value="getEntries()[index]?.bis ?? ''" label="Bis" type="month" @update:model-value="updateEntry(index, 'bis', $event)" />
        </div>
        <Textarea :model-value="getEntries()[index]?.beschreibung ?? ''" label="Beschreibung" rows="2" @update:model-value="updateEntry(index, 'beschreibung', $event)" />
      </div>
    </template>
  </SectionEntryList>
</template>
