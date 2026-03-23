<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  class?: string
  destructive?: boolean
}>()
</script>

<template>
  <button
    :class="cn(
      'relative flex w-full cursor-pointer select-none items-center gap-2 rounded-md px-2 py-1.5 text-sm outline-none transition-colors hover:bg-white/5',
      destructive ? 'text-red-400 hover:bg-red-500/10' : 'text-foreground',
      $props.class
    )"
  >
    <slot />
  </button>
</template>
