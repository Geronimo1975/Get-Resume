<script setup lang="ts">
import type { Template } from '@/types'
import Dialog from '@/components/ui/Dialog.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import { Lock, FileText } from 'lucide-vue-next'

defineProps<{
  open: boolean
  template: Template | null
}>()

defineEmits<{
  'update:open': [value: boolean]
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
  <Dialog :open="open" class="max-w-2xl" @update:open="$emit('update:open', $event)">
    <div v-if="template">
      <div class="mb-4">
        <h2 class="text-lg font-semibold text-foreground">{{ template.name }}</h2>
        <div class="mt-1 flex items-center gap-2">
          <Badge variant="secondary">{{ categoryLabels[template.category] || template.category }}</Badge>
          <Badge v-if="template.is_premium" variant="premium" class="gap-1">
            <Lock class="h-3 w-3" /> Premium
          </Badge>
        </div>
      </div>

      <!-- Preview -->
      <div class="aspect-[210/297] bg-muted rounded-lg overflow-hidden mb-4">
        <img
          v-if="template.thumbnail"
          :src="template.thumbnail"
          :alt="template.name"
          class="h-full w-full object-contain"
        />
        <div v-else class="flex h-full items-center justify-center">
          <FileText class="h-16 w-16 text-muted-foreground/30" />
        </div>
      </div>

      <p v-if="template.description" class="text-sm text-muted-foreground mb-4">
        {{ template.description }}
      </p>

      <div class="flex justify-end gap-3">
        <Button variant="outline" @click="$emit('update:open', false)">
          Schlieflen
        </Button>
        <Button @click="$emit('apply')">
          Vorlage verwenden
        </Button>
      </div>
    </div>
  </Dialog>
</template>
