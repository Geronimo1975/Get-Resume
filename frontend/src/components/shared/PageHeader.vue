<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between mb-6">
    <div>
      <h1 class="font-mono text-2xl font-bold tracking-tight text-foreground">{{ title }}</h1>
      <p v-if="description" class="text-sm text-muted-foreground mt-1">{{ description }}</p>
    </div>
    <div class="flex items-center gap-2 mt-3 sm:mt-0">
      <slot name="actions" />
    </div>
  </div>
</template>
