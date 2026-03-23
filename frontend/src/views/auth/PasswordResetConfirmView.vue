<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { resetPasswordConfirmApi } from '@/api/auth'
import { CheckCircle2 } from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardFooter from '@/components/ui/CardFooter.vue'

const route = useRoute()

const password1 = ref('')
const password2 = ref('')
const loading = ref(false)
const success = ref(false)
const error = ref('')

async function handleSubmit() {
  error.value = ''

  if (password1.value !== password2.value) {
    error.value = 'Passwörter stimmen nicht überein.'
    return
  }

  loading.value = true
  try {
    await resetPasswordConfirmApi({
      uid: route.params.uid as string,
      token: route.params.token as string,
      new_password1: password1.value,
      new_password2: password2.value,
    })
    success.value = true
  } catch (e: unknown) {
    const err = e as { response?: { data?: Record<string, string[]> } }
    const data = err.response?.data
    error.value =
      data?.new_password1?.[0] ??
      data?.new_password2?.[0] ??
      data?.token?.[0] ??
      data?.uid?.[0] ??
      'Zurücksetzen fehlgeschlagen. Der Link ist möglicherweise abgelaufen.'
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

            <p class="font-mono text-xs text-indigo-400 mt-4 mb-2 tracking-widest uppercase">// passwort.neu</p>
            <h1 class="font-mono text-2xl font-bold text-foreground">Neues Passwort setzen</h1>
            <p class="mt-2 text-sm text-muted-foreground">
              Geben Sie Ihr neues Passwort ein.
            </p>
          </div>
        </CardHeader>

        <CardContent>
          <!-- Success state -->
          <div v-if="success" class="text-center py-6">
            <div class="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-4">
              <CheckCircle2 class="h-8 w-8 text-emerald-400" />
            </div>
            <h2 class="font-mono text-lg font-bold text-foreground mb-2">Passwort geändert!</h2>
            <p class="text-sm text-muted-foreground">
              Ihr Passwort wurde erfolgreich zurückgesetzt. Sie können sich jetzt anmelden.
            </p>
          </div>

          <template v-else>
            <!-- Error state -->
            <div
              v-if="error"
              class="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400"
            >
              {{ error }}
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-4">
              <Input
                v-model="password1"
                label="Neues Passwort"
                type="password"
                required
                minlength="10"
                autocomplete="new-password"
              />
              <Input
                v-model="password2"
                label="Passwort bestätigen"
                type="password"
                required
                autocomplete="new-password"
              />
              <Button type="submit" class="w-full glow-sm transition-all hover:glow-md" :loading="loading">
                Passwort speichern
              </Button>
            </form>
          </template>
        </CardContent>

        <CardFooter class="justify-center">
          <RouterLink
            to="/login"
            class="text-sm text-indigo-400 hover:text-indigo-300 hover:underline transition-colors font-medium"
          >
            Zurück zur Anmeldung
          </RouterLink>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
