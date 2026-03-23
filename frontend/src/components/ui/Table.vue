<script setup lang="ts">
import { cn } from '@/lib/cn'

defineProps<{ class?: string }>()
</script>

<template>
  <div class="relative w-full overflow-auto">
    <table :class="cn('w-full caption-bottom text-sm [&_thead_tr]:border-b [&_thead_tr]:border-white/[0.06] [&_tbody_tr]:border-b [&_tbody_tr]:border-white/[0.04] [&_tbody_tr:last-child]:border-0 [&_tbody_tr:nth-child(even)]:bg-white/[0.02] [&_th]:px-4 [&_th]:py-3 [&_th]:text-left [&_th]:text-xs [&_th]:font-medium [&_th]:text-zinc-400 [&_th]:uppercase [&_th]:tracking-wider [&_td]:px-4 [&_td]:py-3 [&_td]:text-foreground', $props.class)">
      <slot />
    </table>
  </div>
</template>
