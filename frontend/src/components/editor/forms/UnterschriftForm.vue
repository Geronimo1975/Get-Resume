<script setup lang="ts">
import type { UnterschriftContent } from '@/types'
import Input from '@/components/ui/Input.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

function getData(): Partial<UnterschriftContent> {
  return props.content as Partial<UnterschriftContent>
}

function update(field: keyof UnterschriftContent, value: string) {
  emit('update', { ...props.content, [field]: value })
}
</script>

<template>
  <div class="space-y-4">
    <Input :model-value="getData().ort ?? ''" label="Ort" @update:model-value="update('ort', $event)" />
    <Input :model-value="getData().datum ?? ''" label="Datum" type="date" @update:model-value="update('datum', $event)" />
    <p class="text-xs text-muted-foreground">
      Die Unterschrift wird auf dem Lebenslauf unter dem Ort und Datum angezeigt.
    </p>
  </div>
</template>
