<script setup lang="ts">
import Toast from './Toast.vue'
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()
</script>

<template>
  <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-full max-w-sm pointer-events-none">
    <TransitionGroup name="toast">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :title="toast.title"
        :description="toast.description"
        :variant="toast.variant"
        @close="dismiss(toast.id)"
      />
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from { opacity: 0; transform: translateX(100%); }
.toast-leave-to { opacity: 0; transform: translateX(100%); }
</style>
