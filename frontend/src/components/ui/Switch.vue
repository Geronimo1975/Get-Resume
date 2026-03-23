<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  modelValue?: boolean
  label?: string
  class?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<template>
  <label :class="cn('flex items-center gap-3 cursor-pointer', $props.class)">
    <button
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :class="[
        'relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950',
        modelValue ? 'bg-indigo-500' : 'bg-zinc-700'
      ]"
      @click="emit('update:modelValue', !modelValue)"
    >
      <span
        :class="[
          'pointer-events-none block h-5 w-5 rounded-full bg-white shadow-lg ring-0 transition-transform',
          modelValue ? 'translate-x-5' : 'translate-x-0'
        ]"
      />
    </button>
    <span v-if="label" class="text-sm text-foreground">{{ label }}</span>
  </label>
</template>
