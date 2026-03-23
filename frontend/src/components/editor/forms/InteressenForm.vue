<script setup lang="ts">
import { ref } from 'vue'
import type { InteressenContent } from '@/types'
import { X, Plus } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'

const props = defineProps<{
  content: Record<string, unknown>
}>()

const emit = defineEmits<{
  update: [content: Record<string, unknown>]
}>()

const newInterest = ref('')

function getInterests(): string[] {
  return ((props.content as unknown as InteressenContent).interessen ?? []) as string[]
}

function addInterest() {
  const val = newInterest.value.trim()
  if (!val) return
  const interests = [...getInterests(), val]
  emit('update', { ...props.content, interessen: interests })
  newInterest.value = ''
}

function removeInterest(index: number) {
  const interests = getInterests().filter((_, i) => i !== index)
  emit('update', { ...props.content, interessen: interests })
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addInterest()
  }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex flex-wrap gap-2">
      <span
        v-for="(interest, index) in getInterests()"
        :key="index"
        class="inline-flex items-center gap-1 rounded-full bg-muted px-3 py-1 text-sm"
      >
        {{ interest }}
        <button
          type="button"
          class="rounded-full hover:bg-gray-300 p-0.5 transition-colors"
          @click="removeInterest(index)"
        >
          <X class="h-3 w-3" />
        </button>
      </span>
    </div>

    <div class="flex gap-2">
      <input
        v-model="newInterest"
        class="flex h-10 flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        placeholder="Interesse eingeben und Enter drucken"
        @keydown="onKeydown"
      />
      <Button variant="outline" size="icon" type="button" @click="addInterest">
        <Plus class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>
