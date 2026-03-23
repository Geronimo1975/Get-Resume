<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  class?: string
}>()
</script>

<template>
  <label :class="cn('text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70', $props.class)">
    <slot />
  </label>
</template>
