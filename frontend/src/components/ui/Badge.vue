<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/cn'
import { cva, type VariantProps } from 'class-variance-authority'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary-500/10 text-primary-400 border border-primary-500/20',
        secondary: 'bg-zinc-800 text-zinc-300 border border-white/[0.06]',
        outline: 'border-white/10 text-foreground',
        destructive: 'bg-red-500/10 text-red-400 border border-red-500/20',
        success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
        warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
        premium: 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border border-amber-500/20',
      },
    },
    defaultVariants: { variant: 'default' },
  }
)

type BadgeVariants = VariantProps<typeof badgeVariants>

const props = withDefaults(defineProps<{
  variant?: NonNullable<BadgeVariants['variant']>
  class?: string
}>(), {
  variant: 'default',
})

const classes = computed(() => cn(badgeVariants({ variant: props.variant }), props.class))
</script>

<template>
  <span :class="classes"><slot /></span>
</template>
