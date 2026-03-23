<script setup lang="ts">
import { Plus, Trash2, GripVertical } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'

defineProps<{
  entries: Record<string, unknown>[]
  addLabel?: string
}>()

const emit = defineEmits<{
  add: []
  remove: [index: number]
}>()
</script>

<template>
  <div class="space-y-4">
    <div
      v-for="(_, index) in entries"
      :key="index"
      class="relative rounded-lg border border-border p-4"
    >
      <div class="flex items-start gap-2">
        <GripVertical class="mt-1 h-4 w-4 shrink-0 cursor-grab text-muted-foreground/50" />
        <div class="flex-1">
          <slot :index="index" :entry="entries[index]" />
        </div>
        <button
          type="button"
          class="shrink-0 rounded-md p-1 text-muted-foreground hover:text-destructive transition-colors"
          @click="emit('remove', index)"
          aria-label="Entfernen"
        >
          <Trash2 class="h-4 w-4" />
        </button>
      </div>
    </div>

    <Button variant="outline" size="sm" type="button" class="w-full" @click="emit('add')">
      <Plus class="h-4 w-4" />
      {{ addLabel || 'Eintrag hinzufugen' }}
    </Button>
  </div>
</template>
