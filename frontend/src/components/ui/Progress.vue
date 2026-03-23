<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  value: number
  max?: number
  class?: string
}>()
</script>

<template>
  <div
    role="progressbar"
    :aria-valuenow="value"
    :aria-valuemax="max ?? 100"
    :class="cn('relative h-2 w-full overflow-hidden rounded-full bg-zinc-800', $props.class)"
  >
    <div
      class="h-full bg-indigo-500 transition-all duration-300"
      :style="{ width: `${Math.min(100, (value / (max ?? 100)) * 100)}%` }"
    />
  </div>
</template>
