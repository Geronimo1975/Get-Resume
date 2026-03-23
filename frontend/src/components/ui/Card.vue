<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{ class?: string }>()
</script>

<template>
  <div :class="cn('rounded-xl border border-white/[0.06] bg-card text-card-foreground', $props.class)">
    <slot />
  </div>
</template>
