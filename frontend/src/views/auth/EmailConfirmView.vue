<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/client'
import { CheckCircle2, XCircle } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardFooter from '@/components/ui/CardFooter.vue'

const route = useRoute()

const status = ref<'loading' | 'success' | 'error'>('loading')
const errorMessage = ref('')

onMounted(async () => {
  const key = route.params.key as string
  if (!key) {
    status.value = 'error'
    errorMessage.value = 'Kein Bestätigungsschlüssel gefunden.'
    return
  }

  try {
    await api.post('/auth/registration/verify-email/', { key })
    status.value = 'success'
  } catch {
    status.value = 'error'
    errorMessage.value = 'Der Bestätigungslink ist ungültig oder abgelaufen.'
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4 relative">
    <!-- Background pattern -->
    <div class="absolute inset-0 bg-dots opacity-20"></div>

    <!-- Gradient orbs -->
    <div class="absolute top-1/4 left-1/4 h-64 w-64 rounded-full bg-indigo-500/8 blur-3xl animate-float pointer-events-none"></div>
    <div class="absolute bottom-1/4 right-1/4 h-48 w-48 rounded-full bg-violet-500/8 blur-3xl animate-float-delayed pointer-events-none"></div>

    <div class="relative w-full max-w-md animate-fade-in">
      <Card class="border-white/[0.06] bg-card glow-border">
        <CardHeader>
          <div class="text-center">
            <!-- Terminal logo -->
            <RouterLink to="/" class="inline-flex items-center gap-2.5 group justify-center mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-mono text-sm font-bold transition-all group-hover:bg-indigo-500/20">
                &gt;_
              </div>
              <span class="font-mono text-lg font-bold">Get<span class="text-gradient">Resume</span></span>
            </RouterLink>

            <p class="font-mono text-xs text-indigo-400 mt-4 mb-2 tracking-widest uppercase">// email.bestaetigen</p>
            <h1 class="font-mono text-2xl font-bold text-foreground">E-Mail Bestätigung</h1>
          </div>
        </CardHeader>

        <CardContent>
          <!-- Loading -->
          <div v-if="status === 'loading'" class="text-center py-6">
            <div class="inline-flex h-12 w-12 items-center justify-center rounded-full border border-indigo-500/20 bg-indigo-500/10 mb-4 animate-pulse">
              <div class="h-5 w-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-sm text-muted-foreground">E-Mail wird bestätigt...</p>
          </div>

          <!-- Success -->
          <div v-else-if="status === 'success'" class="text-center py-6">
            <div class="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-4">
              <CheckCircle2 class="h-8 w-8 text-emerald-400" />
            </div>
            <h2 class="font-mono text-lg font-bold text-foreground mb-2">E-Mail bestätigt!</h2>
            <p class="text-sm text-muted-foreground">
              Ihre E-Mail-Adresse wurde erfolgreich bestätigt. Sie können sich jetzt anmelden.
            </p>
          </div>

          <!-- Error -->
          <div v-else class="text-center py-6">
            <div class="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-red-500/10 border border-red-500/20 mb-4">
              <XCircle class="h-8 w-8 text-red-400" />
            </div>
            <h2 class="font-mono text-lg font-bold text-foreground mb-2">Bestätigung fehlgeschlagen</h2>
            <p class="text-sm text-muted-foreground">
              {{ errorMessage }}
            </p>
          </div>
        </CardContent>

        <CardFooter class="justify-center">
          <RouterLink to="/login">
            <Button variant="outline">Zur Anmeldung</Button>
          </RouterLink>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
