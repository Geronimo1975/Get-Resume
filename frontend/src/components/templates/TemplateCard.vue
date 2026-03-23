<script setup lang="ts">
import type { Template } from '@/types'
import Badge from '@/components/ui/Badge.vue'
import { Lock, FileText } from 'lucide-vue-next'

defineProps<{
  template: Template
}>()

defineEmits<{
  preview: []
  apply: []
}>()

const categoryLabels: Record<string, string> = {
  klassisch: 'Klassisch',
  modern: 'Modern',
  kreativ: 'Kreativ',
  akademisch: 'Akademisch',
  it_tech: 'IT & Tech',
  student: 'Student',
}
</script>

<template>
  <div
    class="group relative cursor-pointer overflow-hidden rounded-xl border border-white/[0.06] bg-card/50 transition-all duration-300 hover:border-white/[0.12] hover:bg-card/80"
    @click="$emit('preview')"
  >
    <!-- Thumbnail -->
    <div class="relative aspect-[210/297] bg-muted">
      <img
        v-if="template.thumbnail"
        :src="template.thumbnail"
        :alt="template.name"
        class="h-full w-full object-cover"
      />
      <div v-else class="flex h-full items-center justify-center">
        <FileText class="h-12 w-12 text-zinc-700" />
      </div>

      <!-- Hover overlay -->
      <div class="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-all duration-300">
        <button class="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white shadow-lg">
          Vorschau
        </button>
      </div>

      <!-- Premium lock -->
      <div v-if="template.is_premium" class="absolute top-2 right-2">
        <Badge variant="premium" class="gap-1">
          <Lock class="h-3 w-3" />
          Premium
        </Badge>
      </div>
    </div>

    <!-- Info -->
    <div class="p-3">
      <p class="font-mono font-medium text-foreground text-sm truncate">{{ template.name }}</p>
      <Badge variant="secondary" class="mt-1 text-xs">
        {{ categoryLabels[template.category] || template.category }}
      </Badge>
    </div>
  </div>
</template>
