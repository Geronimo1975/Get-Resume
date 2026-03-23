<script setup lang="ts">
defineProps<{
  open: boolean
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  destructive?: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: []
}>()

function onConfirm() {
  emit('confirm')
  emit('update:open', false)
}
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" @click="emit('update:open', false)" />
        <div class="relative z-50 w-full max-w-md rounded-xl bg-[#111113] border border-white/[0.08] p-6 shadow-xl">
          <h3 class="text-lg font-semibold text-foreground">{{ title }}</h3>
          <p v-if="description" class="mt-2 text-sm text-zinc-400">{{ description }}</p>
          <div class="mt-6 flex justify-end gap-3">
            <button
              class="rounded-md px-4 py-2 text-sm font-medium text-zinc-400 hover:bg-white/5 hover:text-foreground transition-colors"
              @click="emit('update:open', false)"
            >
              {{ cancelLabel || 'Abbrechen' }}
            </button>
            <button
              :class="[
                'rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors',
                destructive ? 'bg-red-500/80 hover:bg-red-600' : 'bg-primary-500 hover:bg-primary-600'
              ]"
              @click="onConfirm"
            >
              {{ confirmLabel || 'Bestatigen' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active,
.dialog-leave-active { transition: opacity 0.15s ease; }
.dialog-enter-from,
.dialog-leave-to { opacity: 0; }
</style>
