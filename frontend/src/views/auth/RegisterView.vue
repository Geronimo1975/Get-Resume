<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ArrowRight, CheckCircle2 } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Checkbox from '@/components/ui/Checkbox.vue'
import Progress from '@/components/ui/Progress.vue'

const auth = useAuthStore()
const router = useRouter()

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  password1: '',
  password2: '',
  privacy_accepted: false,
})
const error = ref('')
const loading = ref(false)
const verificationSent = ref(false)

const passwordStrength = computed(() => {
  const p = form.value.password1
  let score = 0
  if (p.length >= 10) score += 25
  if (/[A-Z]/.test(p)) score += 25
  if (/[0-9]/.test(p)) score += 25
  if (/[^A-Za-z0-9]/.test(p)) score += 25
  return score
})

const strengthLabel = computed(() => {
  if (passwordStrength.value <= 25) return 'Schwach'
  if (passwordStrength.value <= 50) return 'Mittel'
  if (passwordStrength.value <= 75) return 'Gut'
  return 'Stark'
})

const strengthColor = computed(() => {
  if (passwordStrength.value <= 25) return 'text-red-500'
  if (passwordStrength.value <= 50) return 'text-amber-500'
  if (passwordStrength.value <= 75) return 'text-blue-500'
  return 'text-emerald-500'
})

async function handleRegister() {
  error.value = ''

  if (!form.value.privacy_accepted) {
    error.value = 'Sie mussen die Datenschutzerklarung akzeptieren.'
    return
  }

  if (form.value.password1 !== form.value.password2) {
    error.value = 'Passworter stimmen nicht uberein.'
    return
  }

  loading.value = true
  try {
    const result = await auth.register({
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      password1: form.value.password1,
      password2: form.value.password2,
    })
    if (result === 'verified') {
      router.push('/app')
    } else {
      verificationSent.value = true
    }
  } catch (e: unknown) {
    const err = e as { response?: { data?: Record<string, string[]> } }
    const data = err.response?.data
    error.value = data?.email?.[0] ?? data?.password1?.[0] ?? data?.non_field_errors?.[0] ?? 'Registrierung fehlgeschlagen.'
  } finally {
    loading.value = false
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
      <div class="absolute top-32 right-10 h-56 w-56 rounded-full bg-violet-500/10 blur-3xl animate-float"></div>
      <div class="absolute bottom-32 left-10 h-72 w-72 rounded-full bg-indigo-500/10 blur-3xl animate-float-delayed"></div>
      <div class="absolute top-1/4 left-1/3 h-48 w-48 rounded-full bg-cyan-500/5 blur-3xl animate-float-slow"></div>

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
          <p class="font-mono text-xs text-indigo-400 mb-3 tracking-widest uppercase">// auth.register</p>
          <h2 class="font-mono text-3xl font-bold text-foreground leading-tight">
            Starten Sie Ihre<br />
            <span class="text-gradient">Karriere</span>
          </h2>
          <p class="mt-4 text-zinc-400 leading-relaxed text-sm">
            Registrieren Sie sich kostenlos und erstellen Sie in wenigen Minuten professionelle Bewerbungsunterlagen.
          </p>

          <!-- Benefits -->
          <div class="mt-8 space-y-3">
            <div
              v-for="benefit in [
                'Kostenloser Lebenslauf',
                '30+ professionelle Vorlagen',
                'KI-optimierte Formulierungen',
                'PDF-Export in Druckqualitat',
                'DSGVO-konform & sicher',
              ]"
              :key="benefit"
              class="flex items-center gap-3"
            >
              <CheckCircle2 class="h-4 w-4 text-emerald-400 shrink-0" />
              <span class="text-zinc-300 text-sm">{{ benefit }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <p class="font-mono text-xs text-zinc-600">&copy; 2026 GetResume GmbH</p>
      </div>
    </div>

    <!-- Right: register form -->
    <div class="flex-1 flex items-center justify-center bg-background relative overflow-y-auto">
      <div class="absolute inset-0 bg-dots opacity-20"></div>

      <div class="relative w-full max-w-md px-8 py-12">
        <!-- Mobile logo: terminal style -->
        <RouterLink to="/" class="lg:hidden flex items-center gap-2.5 mb-8">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-mono text-sm font-bold glow-border">
            &gt;_
          </div>
          <span class="font-mono text-lg font-bold">Get<span class="text-gradient">Resume</span></span>
        </RouterLink>

        <!-- Email verification sent screen -->
        <div v-if="verificationSent" class="animate-fade-in text-center py-8">
          <div class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
            <CheckCircle2 class="h-8 w-8 text-emerald-400" />
          </div>
          <p class="font-mono text-xs text-emerald-400 mb-2 tracking-widest uppercase">// email.bestatigen</p>
          <h1 class="font-mono text-2xl font-bold text-foreground">E-Mail bestatigen</h1>
          <p class="mt-3 text-muted-foreground text-sm max-w-xs mx-auto">
            Wir haben eine Bestatigungs-E-Mail an
            <span class="text-foreground font-medium">{{ form.email }}</span>
            gesendet. Bitte klicken Sie auf den Link in der E-Mail.
          </p>
          <div class="mt-8 space-y-3">
            <RouterLink to="/login">
              <Button variant="outline" class="w-full">Zur Anmeldung</Button>
            </RouterLink>
            <p class="text-xs text-zinc-500">Keine E-Mail erhalten? Prufen Sie Ihren Spam-Ordner.</p>
          </div>
        </div>

        <!-- Registration form -->
        <template v-else>
        <div class="animate-fade-in">
          <p class="font-mono text-xs text-indigo-400 mb-2 tracking-widest uppercase">// konto.erstellen</p>
          <h1 class="font-mono text-3xl font-bold text-foreground">Konto erstellen</h1>
          <p class="mt-2 text-muted-foreground text-sm">Erstellen Sie Ihren professionellen Lebenslauf</p>
        </div>

        <div class="animate-fade-in-up mt-8">
          <!-- Error state -->
          <div
            v-if="error"
            class="mb-6 rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400"
          >
            {{ error }}
          </div>

          <form @submit.prevent="handleRegister" class="space-y-5">
            <div class="grid grid-cols-2 gap-4">
              <Input v-model="form.first_name" label="Vorname" required autocomplete="given-name" />
              <Input v-model="form.last_name" label="Nachname" required autocomplete="family-name" />
            </div>

            <Input
              v-model="form.email"
              label="E-Mail"
              type="email"
              placeholder="name@beispiel.de"
              required
              autocomplete="email"
            />

            <div>
              <Input
                v-model="form.password1"
                label="Passwort"
                type="password"
                required
                minlength="10"
                autocomplete="new-password"
              />
              <!-- Password strength indicator -->
              <div v-if="form.password1" class="mt-2.5 space-y-1.5">
                <Progress :value="passwordStrength" class="h-1.5" />
                <p :class="['font-mono text-xs font-medium', strengthColor]">{{ strengthLabel }}</p>
              </div>
            </div>

            <Input
              v-model="form.password2"
              label="Passwort bestatigen"
              type="password"
              required
              autocomplete="new-password"
            />

            <Checkbox v-model="form.privacy_accepted">
              Ich akzeptiere die
              <RouterLink
                to="/datenschutz"
                class="text-indigo-400 hover:text-indigo-300 hover:underline font-medium transition-colors"
                target="_blank"
              >Datenschutzerklarung</RouterLink>
              und die
              <RouterLink
                to="/agb"
                class="text-indigo-400 hover:text-indigo-300 hover:underline font-medium transition-colors"
                target="_blank"
              >AGB</RouterLink>.
            </Checkbox>

            <Button
              type="submit"
              class="w-full h-11 glow-sm transition-all hover:glow-md"
              :loading="loading"
            >
              Kostenlos registrieren
              <ArrowRight class="ml-2 h-4 w-4" />
            </Button>
          </form>

          <div class="mt-8 text-center">
            <p class="text-sm text-muted-foreground">
              Bereits ein Konto?
              <RouterLink
                to="/login"
                class="font-semibold text-indigo-400 hover:text-indigo-300 hover:underline transition-colors"
              >
                Anmelden
              </RouterLink>
            </p>
          </div>
        </div>
        </template>
      </div>
    </div>
  </div>
</template>
