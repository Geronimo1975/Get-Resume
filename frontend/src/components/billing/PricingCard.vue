<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import { Check, Sparkles } from 'lucide-vue-next'

defineProps<{
  name: string
  price: string
  period: string
  features: string[]
  highlighted?: boolean
  current?: boolean
}>()

defineEmits<{
  select: []
}>()
</script>

<template>
  <div :class="[
    'relative flex flex-col rounded-2xl border p-6 transition-all duration-300',
    highlighted
      ? 'border-indigo-500/30 bg-card glow-border hover:border-indigo-500/40'
      : 'border-white/[0.06] bg-card/50 hover:border-white/[0.1] hover:bg-card/80',
  ]">
    <!-- Highlighted glow -->
    <div v-if="highlighted" class="absolute -inset-px rounded-2xl bg-gradient-to-b from-indigo-500/10 via-indigo-500/5 to-transparent -z-10 blur-sm"></div>

    <!-- Popular badge -->
    <div v-if="highlighted" class="absolute -top-3.5 left-1/2 -translate-x-1/2">
      <div class="flex items-center gap-1.5 rounded-full bg-indigo-500 px-4 py-1.5 text-xs font-mono font-semibold text-white shadow-lg shadow-indigo-500/25">
        <Sparkles class="h-3 w-3" />
        Beliebteste
      </div>
    </div>

    <h3 class="font-mono text-lg font-semibold text-foreground">{{ name }}</h3>
    <div class="mt-3">
      <span class="font-mono text-4xl font-bold text-foreground">{{ price }}</span>
      <span class="text-lg text-zinc-500 ml-1">&euro;</span>
      <span v-if="period" class="text-sm text-zinc-500 ml-1">{{ period }}</span>
    </div>
    <p class="mt-1.5 text-xs text-zinc-600 font-mono">inkl. 19% MwSt</p>

    <div class="my-6 h-px bg-gradient-to-r from-transparent via-white/[0.06] to-transparent"></div>

    <ul class="flex-1 space-y-3">
      <li v-for="feature in features" :key="feature" class="flex items-start gap-2.5 text-sm text-zinc-300">
        <div class="flex h-5 w-5 items-center justify-center rounded-md bg-emerald-500/10 border border-emerald-500/20 shrink-0 mt-0.5">
          <Check class="h-3 w-3 text-emerald-400" />
        </div>
        {{ feature }}
      </li>
    </ul>

    <Button
      :variant="current ? 'secondary' : highlighted ? 'default' : 'outline'"
      :class="'mt-6 w-full h-11 transition-all duration-200' + (highlighted && !current ? ' glow-sm hover:glow-md' : '')"
      :disabled="current"
      @click="$emit('select')"
    >
      {{ current ? 'Aktueller Plan' : 'Auswahlen' }}
    </Button>
  </div>
</template>
