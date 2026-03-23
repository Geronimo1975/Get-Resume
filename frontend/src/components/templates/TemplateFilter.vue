<script setup lang="ts">
import { TEMPLATE_CATEGORIES } from '@/lib/constants'
import Tabs from '@/components/ui/Tabs.vue'

defineProps<{
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <Tabs
    :model-value="modelValue"
    :tabs="TEMPLATE_CATEGORIES"
    @update:model-value="$emit('update:modelValue', $event)"
  />
</template>
