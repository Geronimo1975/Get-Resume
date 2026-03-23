<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { FileText, ArrowRight, Shield, Sparkles } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const emailNotVerified = ref(false)
const resendLoading = ref(false)
const resendSuccess = ref(false)

async function handleLogin() {
  error.value = ''
  emailNotVerified.value = false
  resendSuccess.value = false
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = (route.query.redirect as string) || '/app'
    router.push(redirect)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { non_field_errors?: string[] } } }
    const msg = err.response?.data?.non_field_errors?.[0] ?? ''
    // Detect unverified email error from allauth/dj-rest-auth
    if (msg.toLowerCase().includes('e-mail') && msg.toLowerCase().includes('verif')) {
      emailNotVerified.value = true
      error.value = 'Ihre E-Mail-Adresse wurde noch nicht bestätigt.'
    } else {
      error.value = msg || 'Anmeldung fehlgeschlagen.'
    }
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  resendLoading.value = true
  try {
    await auth.resendVerification(email.value)
    resendSuccess.value = true
  } catch {
    // Silently succeed — don't reveal whether email exists
    resendSuccess.value = true
  } finally {
    resendLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left: branded visual panel (hidden on mobile) -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-[#0d0d11]">
      <!-- Grid pattern -->
      <div class="absolute inset-0 bg-grid opacity-30"></div>

      <!-- Gradient orbs -->
      <div class="absolute top-20 left-10 h-48 w-48 rounded-full bg-indigo-500/10 blur-3xl animate-float"></div>
      <div class="absolute bottom-20 right-10 h-64 w-64 rounded-full bg-violet-500/10 blur-3xl animate-float-delayed"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-80 w-80 rounded-full bg-indigo-600/5 blur-3xl animate-float-slow"></div>

      <div class="relative flex flex-col justify-between p-12 w-full">
        <!-- Logo: terminal style -->
        <RouterLink to="/" class="flex items-center gap-2.5 group">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-mono text-sm font-bold glow-border transition-all group-hover:bg-indigo-500/20">
            &gt;_
          </div>
          <span class="font-mono text-lg font-bold text-zinc-100 tracking-tight">GetResume</span>
        </RouterLink>

        <!-- Content -->
        <div class="max-w-md">
          <p class="font-mono text-xs text-indigo-400 mb-3 tracking-widest uppercase">// auth.login</p>
          <h2 class="font-mono text-3xl font-bold text-foreground leading-tight">
            Willkommen<br />
            <span class="text-gradient">zuruck</span>
          </h2>
          <p class="mt-4 text-zinc-400 leading-relaxed text-sm">
            Uber 10.000 Bewerber vertrauen GetResume fur ihre Karriere. DSGVO-konform und in Deutschland gehostet.
          </p>

          <!-- Feature list -->
          <div class="mt-8 space-y-4">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg border border-indigo-500/20 bg-indigo-500/10 shrink-0">
                <FileText class="h-4 w-4 text-indigo-400" />
              </div>
              <span class="text-zinc-300 text-sm">30+ professionelle Vorlagen</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg border border-indigo-500/20 bg-indigo-500/10 shrink-0">
                <Sparkles class="h-4 w-4 text-indigo-400" />
              </div>
              <span class="text-zinc-300 text-sm">KI-optimierte Texte</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg border border-indigo-500/20 bg-indigo-500/10 shrink-0">
                <Shield class="h-4 w-4 text-indigo-400" />
              </div>
              <span class="text-zinc-300 text-sm">100% DSGVO-konform</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <p class="font-mono text-xs text-zinc-600">&copy; 2026 GetResume GmbH</p>
      </div>
    </div>

    <!-- Right: login form -->
    <div class="flex-1 flex items-center justify-center bg-background relative">
      <div class="absolute inset-0 bg-dots opacity-20"></div>

      <div class="relative w-full max-w-md px-8 py-12">
        <!-- Mobile logo: terminal style -->
        <RouterLink to="/" class="lg:hidden flex items-center gap-2.5 mb-8 group">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-mono text-sm font-bold glow-border">
            &gt;_
          </div>
          <span class="font-mono text-lg font-bold">Get<span class="text-gradient">Resume</span></span>
        </RouterLink>

        <div class="animate-fade-in">
          <p class="font-mono text-xs text-indigo-400 mb-2 tracking-widest uppercase">// anmelden</p>
          <h1 class="font-mono text-3xl font-bold text-foreground">Willkommen zuruck</h1>
          <p class="mt-2 text-muted-foreground text-sm">Melden Sie sich bei Ihrem Konto an</p>
        </div>

        <div class="animate-fade-in-up mt-8">
          <!-- Error state -->
          <div
            v-if="error"
            class="mb-6 rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400"
          >
            <p>{{ error }}</p>
            <!-- Resend verification for unverified emails -->
            <div v-if="emailNotVerified && !resendSuccess" class="mt-3">
              <button
                type="button"
                class="text-indigo-400 hover:text-indigo-300 underline text-xs font-medium transition-colors"
                :disabled="resendLoading"
                @click="handleResend"
              >
                {{ resendLoading ? 'Wird gesendet...' : 'Bestätigungsmail erneut senden' }}
              </button>
            </div>
            <p v-if="resendSuccess" class="mt-2 text-emerald-400 text-xs">
              Bestätigungsmail wurde erneut gesendet. Bitte prüfen Sie Ihren Posteingang.
            </p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-5">
            <Input
              v-model="email"
              label="E-Mail"
              type="email"
              placeholder="name@beispiel.de"
              required
              autocomplete="email"
            />
            <div>
              <Input
                v-model="password"
                label="Passwort"
                type="password"
                required
                autocomplete="current-password"
              />
              <RouterLink
                to="/passwort-vergessen"
                class="mt-1.5 inline-block text-xs text-indigo-400 hover:text-indigo-300 hover:underline font-medium transition-colors"
              >
                Passwort vergessen?
              </RouterLink>
            </div>
            <Button
              type="submit"
              class="w-full h-11 glow-sm transition-all hover:glow-md"
              :loading="loading"
            >
              Anmelden
              <ArrowRight class="ml-2 h-4 w-4" />
            </Button>
          </form>

          <div class="mt-8 text-center">
            <p class="text-sm text-muted-foreground">
              Noch kein Konto?
              <RouterLink
                to="/register"
                class="font-semibold text-indigo-400 hover:text-indigo-300 hover:underline transition-colors"
              >
                Kostenlos registrieren
              </RouterLink>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
