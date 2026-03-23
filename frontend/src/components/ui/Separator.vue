<script setup lang="ts">
import { cn } from '@/lib/cn'

const props = withDefaults(defineProps<{
  orientation?: 'horizontal' | 'vertical'
  class?: string
}>(), {
  orientation: 'horizontal',
})
</script>

<template>
  <div
    role="separator"
    :class="cn(
      'shrink-0 bg-white/[0.06]',
      props.orientation === 'horizontal' ? 'h-px w-full' : 'h-full w-px',
      props.class
    )"
  />
</template>
