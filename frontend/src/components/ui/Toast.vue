<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  title: string
  description?: string
  variant?: 'default' | 'destructive' | 'success'
  class?: string
}>()

defineEmits<{ close: [] }>()
</script>

<template>
  <div
    :class="cn(
      'pointer-events-auto relative flex w-full items-start gap-3 overflow-hidden rounded-xl border p-4 shadow-xl backdrop-blur-sm',
      variant === 'destructive' ? 'border-red-500/20 bg-red-500/10 text-red-400' :
      variant === 'success' ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400' :
      'border-white/[0.08] bg-[#111113] text-foreground',
      $props.class
    )"
  >
    <div class="flex-1">
      <p class="text-sm font-semibold">{{ title }}</p>
      <p v-if="description" class="mt-1 text-sm opacity-70">{{ description }}</p>
    </div>
    <button
      class="shrink-0 rounded-sm text-zinc-500 hover:text-foreground transition-colors"
      @click="$emit('close')"
    >
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M18 6L6 18M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
