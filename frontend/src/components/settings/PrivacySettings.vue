<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import Switch from '@/components/ui/Switch.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import { formatDateDE } from '@/lib/formatters'

const auth = useAuthStore()
const { toast } = useToast()

const marketingConsent = ref(false)
const newsletterConsent = ref(false)

onMounted(() => {
  const p = auth.user?.profile
  if (p) {
    marketingConsent.value = p.marketing_consent
    newsletterConsent.value = p.newsletter_consent
  }
})

async function updateConsent(field: 'marketing_consent' | 'newsletter_consent', value: boolean) {
  if (field === 'marketing_consent') marketingConsent.value = value
  else newsletterConsent.value = value

  try {
    await auth.updateProfile({ [field]: value })
    toast({ title: 'Gespeichert', variant: 'success' })
  } catch {
    toast({ title: 'Fehler', variant: 'destructive' })
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Datenschutz & Einwilligungen</h3>
      <p class="text-sm text-muted-foreground">Verwalten Sie Ihre DSGVO-Einwilligungen</p>
    </CardHeader>
    <CardContent class="space-y-4">
      <p v-if="auth.user?.profile?.privacy_accepted_at" class="text-xs text-muted-foreground">
        Datenschutzerklarung akzeptiert am {{ formatDateDE(auth.user.profile.privacy_accepted_at) }}
      </p>

      <Switch
        :model-value="marketingConsent"
        label="Marketing-Einwilligung"
        @update:model-value="updateConsent('marketing_consent', $event)"
      />
      <p class="text-xs text-muted-foreground -mt-2 ml-14">
        Wir durfen Sie uber Produktneuheiten und Angebote per E-Mail informieren.
      </p>

      <Switch
        :model-value="newsletterConsent"
        label="Newsletter"
        @update:model-value="updateConsent('newsletter_consent', $event)"
      />
      <p class="text-xs text-muted-foreground -mt-2 ml-14">
        Regelmafliger Newsletter mit Bewerbungstipps und Karriereratgeber.
      </p>
    </CardContent>
  </Card>
</template>
