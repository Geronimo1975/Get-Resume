<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  open: boolean
  side?: 'left' | 'right'
  class?: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()
</script>

<template>
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="open" class="fixed inset-0 z-50">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" @click="emit('update:open', false)" />
        <div
          :class="cn(
            'fixed top-0 z-50 h-full w-72 bg-[#111113] border-white/[0.08] p-6 shadow-xl transition-transform',
            side === 'right' ? 'right-0 border-l' : 'left-0 border-r',
            $props.class
          )"
        >
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.sheet-enter-active,
.sheet-leave-active { transition: opacity 0.2s ease; }
.sheet-enter-from,
.sheet-leave-to { opacity: 0; }
</style>
