<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{ class?: string }>()
</script>

<template>
  <div :class="cn('relative overflow-auto scrollbar-thin scrollbar-track-transparent scrollbar-thumb-zinc-700 hover:scrollbar-thumb-zinc-600', $props.class)">
    <slot />
  </div>
</template>
