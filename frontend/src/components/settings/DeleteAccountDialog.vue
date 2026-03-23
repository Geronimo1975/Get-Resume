<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { requestGdprDeletion } from '@/api/profile'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Dialog from '@/components/ui/Dialog.vue'

const auth = useAuthStore()
const router = useRouter()
const { toast } = useToast()

const dialogOpen = ref(false)
const confirmation = ref('')
const loading = ref(false)

async function handleDelete() {
  if (confirmation.value !== 'LOSCHEN') return

  loading.value = true
  try {
    await requestGdprDeletion()
    auth.logout()
    router.push('/')
    toast({
      title: 'Konto wird geloscht',
      description: 'Ihr Konto und alle Daten werden innerhalb von 30 Tagen geloscht (Art. 17 DSGVO).',
    })
  } catch {
    toast({ title: 'Fehler', description: 'Anfrage fehlgeschlagen.', variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card class="border-destructive/20">
    <CardHeader>
      <h3 class="text-lg font-semibold text-destructive">Konto loschen</h3>
      <p class="text-sm text-muted-foreground">
        Gemafl Art. 17 DSGVO (Recht auf Loschung) konnen Sie die Loschung Ihres Kontos und aller personenbezogenen Daten beantragen.
        Diese Aktion kann nicht ruckgangig gemacht werden.
      </p>
    </CardHeader>
    <CardContent>
      <Button variant="destructive" @click="dialogOpen = true">
        Konto loschen
      </Button>
    </CardContent>
  </Card>

  <Dialog :open="dialogOpen" @update:open="dialogOpen = $event">
    <h2 class="text-lg font-semibold text-destructive mb-2">Konto unwiderruflich loschen?</h2>
    <p class="text-sm text-muted-foreground mb-4">
      Alle Ihre Dokumente, personlichen Daten und Einstellungen werden dauerhaft geloscht.
      Geben Sie <strong>LOSCHEN</strong> ein, um zu bestatigen.
    </p>
    <Input
      v-model="confirmation"
      placeholder="LOSCHEN eingeben"
      class="mb-4"
    />
    <div class="flex justify-end gap-3">
      <Button variant="outline" @click="dialogOpen = false">Abbrechen</Button>
      <Button
        variant="destructive"
        :disabled="confirmation !== 'LOSCHEN'"
        :loading="loading"
        @click="handleDelete"
      >
        Endgultig loschen
      </Button>
    </div>
  </Dialog>
</template>
