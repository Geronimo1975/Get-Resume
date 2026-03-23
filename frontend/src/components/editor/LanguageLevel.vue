<script setup lang="ts">
import Select from '@/components/ui/Select.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import { SPRACH_NIVEAUS } from '@/lib/constants'

defineProps<{
  niveau: string
  istMuttersprache: boolean
}>()

const emit = defineEmits<{
  'update:niveau': [value: string]
  'update:istMuttersprache': [value: boolean]
}>()
</script>

<template>
  <div class="space-y-2">
    <Select
      :model-value="niveau"
      :options="SPRACH_NIVEAUS"
      :disabled="istMuttersprache"
      placeholder="Niveau wahlen"
      @update:model-value="emit('update:niveau', $event)"
    />
    <Checkbox
      :model-value="istMuttersprache"
      label="Muttersprache"
      @update:model-value="emit('update:istMuttersprache', $event)"
    />
  </div>
</template>
