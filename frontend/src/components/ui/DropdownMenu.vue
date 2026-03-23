<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { cn } from '@/lib/cn'

defineProps<{ class?: string }>()

const open = ref(false)
const triggerRef = ref<HTMLElement>()
const menuRef = ref<HTMLElement>()

function toggle() {
  open.value = !open.value
}

function close() {
  open.value = false
}

function onClickOutside(e: MouseEvent) {
  const target = e.target as Node
  if (!triggerRef.value?.contains(target) && !menuRef.value?.contains(target)) {
    close()
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="relative inline-block">
    <div ref="triggerRef" @click="toggle">
      <slot name="trigger" />
    </div>
    <Transition name="dropdown">
      <div
        v-if="open"
        ref="menuRef"
        :class="cn('absolute right-0 z-50 mt-1 min-w-[8rem] overflow-hidden rounded-xl border border-white/[0.08] bg-[#111113] p-1 shadow-xl backdrop-blur-sm', $props.class)"
        @click="close"
      >
        <slot />
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.1s ease, transform 0.1s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
