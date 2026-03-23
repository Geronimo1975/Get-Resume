<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Button from '@/components/ui/Button.vue'
import { Home, ArrowLeft } from 'lucide-vue-next'
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-background relative overflow-hidden px-4">
    <!-- Background -->
    <div class="absolute inset-0 bg-dots opacity-30"></div>
    <div class="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-indigo-500/[0.06] blur-[120px] animate-pulse-slow"></div>
    <div class="absolute bottom-1/4 right-1/4 h-72 w-72 rounded-full bg-violet-500/[0.05] blur-[120px] animate-pulse-slow" style="animation-delay: 2s"></div>

    <div class="relative text-center animate-fade-in">
      <!-- Large 404 -->
      <p class="text-gradient font-mono text-[10rem] sm:text-[14rem] font-bold leading-none select-none opacity-80">
        404
      </p>

      <h1 class="mt-2 text-2xl sm:text-3xl font-mono font-bold text-foreground">Seite nicht gefunden</h1>
      <p class="mt-3 text-zinc-400 max-w-md mx-auto leading-relaxed">
        Die angeforderte Seite existiert leider nicht oder wurde verschoben.
      </p>

      <div class="mt-10 flex flex-col sm:flex-row items-center justify-center gap-3">
        <RouterLink to="/">
          <Button class="glow-sm hover:glow-md transition-shadow">
            <Home class="h-4 w-4" />
            Zur Startseite
          </Button>
        </RouterLink>
        <Button variant="outline" @click="$router.back()">
          <ArrowLeft class="h-4 w-4" />
          Zuruck
        </Button>
      </div>
    </div>
  </div>
</template>
