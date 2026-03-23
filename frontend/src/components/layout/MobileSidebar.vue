<script setup lang="ts">
import Sheet from '@/components/ui/Sheet.vue'

defineProps<{
  open: boolean
}>()

defineEmits<{
  'update:open': [value: boolean]
}>()
</script>

<template>
  <Sheet :open="open" side="left" @update:open="$emit('update:open', $event)">
    <slot />
  </Sheet>
</template>
