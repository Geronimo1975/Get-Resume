<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  modelValue?: string
  label?: string
  error?: string
  class?: string
  options: { value: string; label: string; disabled?: boolean }[]
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="space-y-1.5">
    <label v-if="label" class="text-sm font-medium text-foreground">{{ label }}</label>
    <select
      :value="modelValue"
      :class="cn(
        'flex h-10 w-full rounded-md border bg-white/[0.02] px-3 py-2 text-sm text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50',
        error
          ? 'border-red-500/50 focus-visible:ring-red-500/40'
          : 'border-white/[0.08] focus-visible:ring-indigo-500/40 focus-visible:border-indigo-500/30',
        $props.class
      )"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="opt in options"
        :key="opt.value"
        :value="opt.value"
        :disabled="opt.disabled"
      >
        {{ opt.label }}
      </option>
    </select>
    <p v-if="error" class="text-xs text-red-400">{{ error }}</p>
  </div>
</template>
