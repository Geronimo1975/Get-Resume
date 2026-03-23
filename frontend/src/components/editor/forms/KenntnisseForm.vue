<script setup lang="ts">
import type { KenntnisEntry, KenntnisseContent } from '@/types'
import Input from '@/components/ui/Input.vue'
import SkillRating from '@/components/editor/SkillRating.vue'
import SectionEntryList from '@/components/editor/SectionEntryList.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getEntries(): KenntnisEntry[] {
  return ((props.content as unknown as KenntnisseContent).eintraege ?? []) as KenntnisEntry[]
}

function updateEntry(index: number, field: keyof KenntnisEntry, value: unknown) {
  const entries = [...getEntries()]
  entries[index] = { ...entries[index], [field]: value } as KenntnisEntry
  emit('update', { ...props.content, eintraege: entries })
}

function addEntry() {
  const entries = [...getEntries()]
  entries.push({ id: crypto.randomUUID(), name: '', kategorie: '', niveau: 3 })
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
    add-label="Kenntnis hinzufugen"
    @add="addEntry"
    @remove="removeEntry"
  >
    <template #default="{ index }">
      <div class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <Input :model-value="getEntries()[index]?.name ?? ''" label="Kenntnis" @update:model-value="updateEntry(index, 'name', $event)" />
          <Input :model-value="getEntries()[index]?.kategorie ?? ''" label="Kategorie" placeholder="z.B. Programmierung" @update:model-value="updateEntry(index, 'kategorie', $event)" />
        </div>
        <div>
          <label class="text-sm font-medium text-foreground mb-1.5 block">Niveau</label>
          <SkillRating :model-value="getEntries()[index]?.niveau ?? 3" @update:model-value="updateEntry(index, 'niveau', $event)" />
        </div>
      </div>
    </template>
  </SectionEntryList>
</template>
