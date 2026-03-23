<script setup lang="ts">
import { ref } from 'vue'
import { cn } from '@/lib/cn'

defineProps<{
  content: string
  class?: string
}>()

const show = ref(false)
</script>

<template>
  <div
    class="relative inline-flex"
    @mouseenter="show = true"
    @mouseleave="show = false"
    @focus="show = true"
    @blur="show = false"
  >
    <slot />
    <Transition name="tooltip">
      <div
        v-if="show"
        role="tooltip"
        :class="cn('absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 rounded-md glass border border-white/[0.08] px-3 py-1.5 text-xs text-foreground shadow-md whitespace-nowrap', $props.class)"
      >
        {{ content }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tooltip-enter-active,
.tooltip-leave-active { transition: opacity 0.1s ease; }
.tooltip-enter-from,
.tooltip-leave-to { opacity: 0; }
</style>
