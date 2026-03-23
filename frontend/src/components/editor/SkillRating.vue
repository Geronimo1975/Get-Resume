<script setup lang="ts">
defineProps<{
  modelValue: number
  max?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

const levels = [1, 2, 3, 4, 5]
</script>

<template>
  <div class="flex gap-1">
    <button
      v-for="level in levels"
      :key="level"
      type="button"
      :class="[
        'h-3 flex-1 rounded-sm transition-colors',
        level <= modelValue ? 'bg-indigo-500' : 'bg-zinc-800'
      ]"
      @click="emit('update:modelValue', level)"
      :aria-label="`Niveau ${level}`"
    />
  </div>
</template>
