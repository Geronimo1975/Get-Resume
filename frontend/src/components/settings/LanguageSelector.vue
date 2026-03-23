<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'

const auth = useAuthStore()
const { toast } = useToast()

const language = ref('de')

onMounted(() => {
  language.value = auth.user?.profile?.preferred_language ?? 'de'
})

async function setLanguage(lang: string) {
  language.value = lang
  try {
    await auth.updateProfile({ preferred_language: lang as 'de' | 'en' })
    toast({ title: 'Gespeichert', description: 'Sprache wurde aktualisiert.', variant: 'success' })
  } catch {
    toast({ title: 'Fehler', variant: 'destructive' })
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Sprache</h3>
      <p class="text-sm text-muted-foreground">Bevorzugte Sprache der Benutzeroberflache</p>
    </CardHeader>
    <CardContent>
      <div class="flex gap-3">
        <button
          v-for="opt in [{ value: 'de', label: 'Deutsch' }, { value: 'en', label: 'English' }]"
          :key="opt.value"
          :class="[
            'rounded-lg border-2 px-6 py-3 text-sm font-medium transition-colors',
            language === opt.value
              ? 'border-indigo-500/50 bg-indigo-500/10 text-indigo-400'
              : 'border-white/[0.08] hover:border-indigo-500/30 text-zinc-400'
          ]"
          @click="setLanguage(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </CardContent>
  </Card>
</template>
