<script setup lang="ts">
import { computed } from 'vue'
import type { PersoenlicheDaten } from '@/types'
import { ANREDE_OPTIONS } from '@/lib/constants'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import PhotoUpload from '@/components/editor/PhotoUpload.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

const data = computed({
  get: () => props.content as Partial<PersoenlicheDaten>,
  set: (val) => emit('update', val as Record<string, unknown>),
})

function update(field: keyof PersoenlicheDaten, value: string) {
  emit('update', { ...props.content, [field]: value })
}
</script>

<template>
  <div class="space-y-4">
    <PhotoUpload :model-value="(data.foto as string) ?? ''" @update:model-value="update('foto', $event)" />

    <Select
      :model-value="(data.anrede as string) ?? ''"
      :options="ANREDE_OPTIONS"
      label="Anrede"
      placeholder="Bitte wahlen"
      @update:model-value="update('anrede', $event)"
    />

    <div class="grid grid-cols-2 gap-4">
      <Input :model-value="data.vorname ?? ''" label="Vorname" @update:model-value="update('vorname', $event)" />
      <Input :model-value="data.nachname ?? ''" label="Nachname" @update:model-value="update('nachname', $event)" />
    </div>

    <div class="grid grid-cols-2 gap-4">
      <Input :model-value="data.geburtsdatum ?? ''" label="Geburtsdatum" type="date" @update:model-value="update('geburtsdatum', $event)" />
      <Input :model-value="data.geburtsort ?? ''" label="Geburtsort" @update:model-value="update('geburtsort', $event)" />
    </div>

    <div class="grid grid-cols-2 gap-4">
      <Input :model-value="data.staatsangehoerigkeit ?? ''" label="Staatsangehorigkeit" @update:model-value="update('staatsangehoerigkeit', $event)" />
      <Input :model-value="data.familienstand ?? ''" label="Familienstand" @update:model-value="update('familienstand', $event)" />
    </div>

    <div class="grid grid-cols-2 gap-4">
      <Input :model-value="data.email ?? ''" label="E-Mail" type="email" @update:model-value="update('email', $event)" />
      <Input :model-value="data.telefon ?? ''" label="Telefon" type="tel" @update:model-value="update('telefon', $event)" />
    </div>

    <Input :model-value="data.strasse ?? ''" label="Strafle" @update:model-value="update('strasse', $event)" />

    <div class="grid grid-cols-3 gap-4">
      <Input :model-value="data.plz ?? ''" label="PLZ" @update:model-value="update('plz', $event)" />
      <Input :model-value="data.stadt ?? ''" label="Stadt" class="col-span-2" @update:model-value="update('stadt', $event)" />
    </div>

    <div class="grid grid-cols-3 gap-4">
      <Input :model-value="data.website ?? ''" label="Website" @update:model-value="update('website', $event)" />
      <Input :model-value="data.linkedin ?? ''" label="LinkedIn" @update:model-value="update('linkedin', $event)" />
      <Input :model-value="data.xing ?? ''" label="XING" @update:model-value="update('xing', $event)" />
    </div>
  </div>
</template>
