<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  open: boolean
  class?: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

function close() {
  emit('update:open', false)
}

function onOverlayClick(e: MouseEvent) {
  if (e.target === e.currentTarget) close()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @keydown="onKeydown"
      >
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" @click="onOverlayClick" />
        <div
          :class="cn('relative z-50 w-full max-w-lg rounded-xl bg-[#111113] border border-white/[0.08] p-6 shadow-xl', $props.class)"
          role="dialog"
          aria-modal="true"
        >
          <slot />
          <button
            class="absolute right-4 top-4 rounded-sm text-zinc-500 hover:text-foreground transition-colors"
            @click="close"
            aria-label="Schliessen"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.15s ease;
}
.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}
</style>
