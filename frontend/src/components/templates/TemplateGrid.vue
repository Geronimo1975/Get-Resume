<script setup lang="ts">
import type { Template } from '@/types'
import TemplateCard from './TemplateCard.vue'

defineProps<{
  templates: Template[]
}>()

defineEmits<{
  preview: [template: Template]
  apply: [template: Template]
}>()
</script>

<template>
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
    <TemplateCard
      v-for="tmpl in templates"
      :key="tmpl.id"
      :template="tmpl"
      @preview="$emit('preview', tmpl)"
      @apply="$emit('apply', tmpl)"
    />
  </div>
</template>
