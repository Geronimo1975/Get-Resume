<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toaster from '@/components/ui/Toaster.vue'
import CookieBanner from '@/components/legal/CookieBanner.vue'
</script>

<template>
  <RouterView />
  <Toaster />
  <CookieBanner />
</template>
