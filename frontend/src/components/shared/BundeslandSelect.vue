<script setup lang="ts">
import type { Bundesland } from '@/types'
import { BUNDESLAENDER } from '@/lib/constants'
import Select from '@/components/ui/Select.vue'

defineProps<{
  modelValue: string
  label?: string
  error?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <Select
    :model-value="modelValue"
    :label="label || 'Bundesland'"
    :options="(BUNDESLAENDER as { value: string; label: string }[])"
    :error="error"
    @update:model-value="$emit('update:modelValue', $event as Bundesland)"
  />
</template>
