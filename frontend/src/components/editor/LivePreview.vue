<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import CvPreviewRenderer from './CvPreviewRenderer.vue'

const containerRef = ref<HTMLElement>()
const scale = ref(0.5)

function updateScale() {
  if (!containerRef.value) return
  const containerWidth = containerRef.value.clientWidth - 32 // padding
  // A4 width in pixels at 96 DPI = 794px
  const a4Width = 794
  scale.value = Math.min(containerWidth / a4Width, 1)
}

let observer: ResizeObserver | null = null

onMounted(() => {
  updateScale()
  if (containerRef.value) {
    observer = new ResizeObserver(updateScale)
    observer.observe(containerRef.value)
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<template>
  <div ref="containerRef" class="flex h-full items-start justify-center overflow-auto bg-gray-100 p-4">
    <div
      class="bg-white shadow-lg origin-top"
      :style="{
        width: '794px',
        minHeight: '1123px',
        transform: `scale(${scale})`,
      }"
    >
      <CvPreviewRenderer />
    </div>
  </div>
</template>
