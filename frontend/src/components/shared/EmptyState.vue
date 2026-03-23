<script setup lang="ts">
import Button from '@/components/ui/Button.vue'

defineProps<{
  title: string
  description: string
  actionLabel?: string
}>()

defineEmits<{
  action: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div class="mb-4 rounded-xl bg-white/[0.03] border border-white/[0.06] p-4">
      <slot name="icon">
        <svg class="h-8 w-8 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </slot>
    </div>
    <h3 class="font-mono text-lg font-semibold text-foreground">{{ title }}</h3>
    <p class="mt-1 max-w-sm text-sm text-muted-foreground">{{ description }}</p>
    <Button v-if="actionLabel" class="mt-4" @click="$emit('action')">
      {{ actionLabel }}
    </Button>
  </div>
</template>
