<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/cn'

const props = withDefaults(defineProps<{
  src?: string
  alt?: string
  fallback?: string
  size?: 'sm' | 'md' | 'lg'
  class?: string
}>(), {
  size: 'md',
})

const sizeClasses = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
}

const initials = computed(() => {
  if (props.fallback) return props.fallback.slice(0, 2).toUpperCase()
  return '?'
})
</script>

<template>
  <div :class="cn('relative flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-indigo-500/10', sizeClasses[size], $props.class)">
    <img v-if="src" :src="src" :alt="alt" class="h-full w-full object-cover" />
    <span v-else class="font-medium text-indigo-400">{{ initials }}</span>
  </div>
</template>
