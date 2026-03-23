<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/cn'

const props = defineProps<{
  modelValue?: string | number
  label?: string
  error?: string
  class?: string
  id?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputId = computed(() => props.id || `input-${Math.random().toString(36).slice(2, 9)}`)
</script>

<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="inputId" class="text-sm font-medium text-foreground">
      {{ label }}
    </label>
    <input
      :id="inputId"
      :value="modelValue"
      :class="cn(
        'flex h-10 w-full rounded-md border bg-white/[0.02] px-3 py-2 text-sm text-foreground transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50',
        error
          ? 'border-red-500/50 focus-visible:ring-red-500/40 focus-visible:border-red-500/50'
          : 'border-white/[0.08] focus-visible:ring-indigo-500/40 focus-visible:border-indigo-500/30',
        props.class
      )"
      v-bind="$attrs"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="text-xs text-red-400">{{ error }}</p>
  </div>
</template>

<script lang="ts">
export default { inheritAttrs: false }
</script>
