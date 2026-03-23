<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{
  modelValue: string
  tabs: { value: string; label: string; count?: number }[]
  class?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div :class="cn('inline-flex h-10 items-center gap-1 rounded-lg bg-zinc-900 border border-white/[0.06] p-1', $props.class)">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      type="button"
      :class="[
        'inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
        modelValue === tab.value
          ? 'bg-zinc-800 text-foreground shadow-sm border border-white/[0.06]'
          : 'text-zinc-400 hover:text-foreground hover:bg-white/5'
      ]"
      @click="emit('update:modelValue', tab.value)"
    >
      {{ tab.label }}
      <span
        v-if="tab.count !== undefined"
        class="ml-1 rounded-full bg-zinc-700 text-zinc-300 px-1.5 py-0.5 text-xs"
      >
        {{ tab.count }}
      </span>
    </button>
  </div>
</template>
