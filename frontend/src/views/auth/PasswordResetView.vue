<script setup lang="ts">
import { ref } from 'vue'
import { resetPasswordApi } from '@/api/auth'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardFooter from '@/components/ui/CardFooter.vue'

const email = ref('')
const loading = ref(false)
const sent = ref(false)
const error = ref('')

async function handleReset() {
  error.value = ''
  loading.value = true
  try {
    await resetPasswordApi(email.value)
    sent.value = true
  } catch {
    error.value = 'Anfrage fehlgeschlagen. Bitte versuchen Sie es erneut.'
  } finally {
    loading.value = false
  }
}
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

            <p class="font-mono text-xs text-indigo-400 mt-4 mb-2 tracking-widest uppercase">// passwort.zuruecksetzen</p>
            <h1 class="font-mono text-2xl font-bold text-foreground">Passwort vergessen</h1>
            <p class="mt-2 text-sm text-muted-foreground">
              Geben Sie Ihre E-Mail-Adresse ein und wir senden Ihnen einen Link zum Zurucksetzen.
            </p>
          </div>
        </CardHeader>

        <CardContent>
          <!-- Success state -->
          <div
            v-if="sent"
            class="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4 text-sm text-emerald-400"
          >
            Falls ein Konto mit dieser E-Mail-Adresse existiert, haben wir Ihnen eine E-Mail mit Anweisungen zum Zurucksetzen gesendet.
          </div>

          <template v-else>
            <!-- Error state -->
            <div
              v-if="error"
              class="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400"
            >
              {{ error }}
            </div>

            <form @submit.prevent="handleReset" class="space-y-4">
              <Input
                v-model="email"
                label="E-Mail"
                type="email"
                placeholder="name@beispiel.de"
                required
                autocomplete="email"
              />
              <Button type="submit" class="w-full glow-sm transition-all hover:glow-md" :loading="loading">
                Link senden
              </Button>
            </form>
          </template>
        </CardContent>

        <CardFooter class="justify-center">
          <RouterLink
            to="/login"
            class="text-sm text-indigo-400 hover:text-indigo-300 hover:underline transition-colors font-medium"
          >
            Zuruck zur Anmeldung
          </RouterLink>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
