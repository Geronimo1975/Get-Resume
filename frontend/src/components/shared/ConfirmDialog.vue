<script setup lang="ts">
import AlertDialog from '@/components/ui/AlertDialog.vue'

defineProps<{
  open: boolean
  title: string
  description?: string
  confirmLabel?: string
  destructive?: boolean
}>()

defineEmits<{
  'update:open': [value: boolean]
  confirm: []
}>()
</script>

<template>
  <AlertDialog
    :open="open"
    :title="title"
    :description="description"
    :confirm-label="confirmLabel"
    :destructive="destructive"
    @update:open="$emit('update:open', $event)"
    @confirm="$emit('confirm')"
  />
</template>
