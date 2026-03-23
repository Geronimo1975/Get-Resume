<script setup lang="ts">
import type { SpracheEntry, SprachenContent } from '@/types'
import Input from '@/components/ui/Input.vue'
import LanguageLevel from '@/components/editor/LanguageLevel.vue'
import SectionEntryList from '@/components/editor/SectionEntryList.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getEntries(): SpracheEntry[] {
  return ((props.content as unknown as SprachenContent).eintraege ?? []) as SpracheEntry[]
}

function updateEntry(index: number, field: keyof SpracheEntry, value: unknown) {
  const entries = [...getEntries()]
  entries[index] = { ...entries[index], [field]: value } as SpracheEntry
  emit('update', { ...props.content, eintraege: entries })
}

function addEntry() {
  const entries = [...getEntries()]
  entries.push({ id: crypto.randomUUID(), sprache: '', niveau: 'B1', ist_muttersprache: false })
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
    add-label="Sprache hinzufugen"
    @add="addEntry"
    @remove="removeEntry"
  >
    <template #default="{ index }">
      <div class="space-y-3">
        <Input :model-value="getEntries()[index]?.sprache ?? ''" label="Sprache" @update:model-value="updateEntry(index, 'sprache', $event)" />
        <LanguageLevel
          :niveau="getEntries()[index]?.niveau ?? 'B1'"
          :ist-muttersprache="getEntries()[index]?.ist_muttersprache ?? false"
          @update:niveau="updateEntry(index, 'niveau', $event)"
          @update:ist-muttersprache="updateEntry(index, 'ist_muttersprache', $event)"
        />
      </div>
    </template>
  </SectionEntryList>
</template>
