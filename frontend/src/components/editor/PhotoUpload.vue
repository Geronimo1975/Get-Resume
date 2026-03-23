<script setup lang="ts">
import { ref } from 'vue'
import { Upload, X } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const dragOver = ref(false)
const MAX_SIZE = 5 * 1024 * 1024 // 5MB

function handleFile(file: File) {
  if (!file.type.startsWith('image/')) return
  if (file.size > MAX_SIZE) {
    alert('Maximale Dateigrofle: 5 MB')
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    emit('update:modelValue', reader.result as string)
  }
  reader.readAsDataURL(file)
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (file) handleFile(file)
}

function onFileInput(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) handleFile(file)
}

function remove() {
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="space-y-2">
    <label class="text-sm font-medium text-foreground">Foto</label>
    <div v-if="props.modelValue" class="relative inline-block">
      <img
        :src="props.modelValue"
        alt="Foto"
        class="h-24 w-20 rounded-md object-cover border border-white/[0.08]"
      />
      <button
        class="absolute -right-2 -top-2 rounded-full bg-destructive p-1 text-white shadow-sm hover:bg-red-600"
        @click="remove"
      >
        <X class="h-3 w-3" />
      </button>
    </div>
    <div
      v-else
      :class="[
        'flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 text-center transition-colors',
        dragOver ? 'border-indigo-400 bg-indigo-500/5' : 'border-white/[0.08]'
      ]"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="onDrop"
    >
      <Upload class="h-6 w-6 text-muted-foreground" />
      <p class="text-xs text-muted-foreground">Bild hierher ziehen oder</p>
      <label>
        <Button variant="outline" size="sm" type="button" as="span">
          Datei wahlen
        </Button>
        <input type="file" accept="image/*" class="sr-only" @change="onFileInput" />
      </label>
      <p class="text-xs text-muted-foreground">Max. 5 MB</p>
    </div>
  </div>
</template>
