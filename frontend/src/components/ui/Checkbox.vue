<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  modelValue?: boolean
  label?: string
  error?: string
  class?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<template>
  <label :class="cn('flex items-start gap-2 cursor-pointer', $props.class)">
    <input
      type="checkbox"
      :checked="modelValue"
      class="mt-0.5 h-4 w-4 rounded border-white/10 bg-white/[0.02] text-indigo-500 checked:bg-indigo-500 checked:border-indigo-500 focus:ring-indigo-500/40 focus:ring-offset-zinc-950"
      @change="emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
    />
    <span class="text-sm text-foreground">
      <slot>{{ label }}</slot>
    </span>
  </label>
  <p v-if="error" class="text-xs text-red-400 mt-1">{{ error }}</p>
</template>
