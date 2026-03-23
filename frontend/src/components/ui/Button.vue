<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/cn'
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950 disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
  {
    variants: {
      variant: {
        default: 'bg-primary-500 text-white hover:bg-primary-600 shadow-sm',
        secondary: 'bg-zinc-800 text-foreground hover:bg-zinc-700',
        outline: 'border border-white/10 bg-transparent text-foreground hover:bg-white/5',
        ghost: 'hover:bg-white/5 text-zinc-400 hover:text-foreground',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-red-600 shadow-sm',
        link: 'text-primary-500 underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3 text-xs',
        lg: 'h-11 rounded-md px-8 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

type ButtonVariants = VariantProps<typeof buttonVariants>

const props = withDefaults(defineProps<{
  variant?: NonNullable<ButtonVariants['variant']>
  size?: NonNullable<ButtonVariants['size']>
  class?: string
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
}>(), {
  variant: 'default',
  size: 'default',
  type: 'button',
})

const classes = computed(() =>
  cn(buttonVariants({ variant: props.variant, size: props.size }), props.class)
)
</script>

<template>
  <button
    :type="type"
    :class="classes"
    :disabled="disabled || loading"
  >
    <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
    <slot />
  </button>
</template>
