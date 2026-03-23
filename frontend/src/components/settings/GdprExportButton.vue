<script setup lang="ts">
import { ref } from 'vue'
import { requestGdprExport } from '@/api/profile'
import { useToast } from '@/composables/useToast'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'

const { toast } = useToast()
const loading = ref(false)

async function handleExport() {
  loading.value = true
  try {
    await requestGdprExport()
    toast({
      title: 'Datenexport angefordert',
      description: 'Sie erhalten eine E-Mail mit Ihren Daten innerhalb von 30 Tagen (Art. 20 DSGVO).',
      variant: 'success',
    })
  } catch {
    toast({ title: 'Fehler', description: 'Anfrage fehlgeschlagen.', variant: 'destructive' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Datenportabilitat</h3>
      <p class="text-sm text-muted-foreground">
        Gemafl Art. 20 DSGVO konnen Sie eine Kopie Ihrer personenbezogenen Daten in einem maschinenlesbaren Format anfordern.
      </p>
    </CardHeader>
    <CardContent>
      <Button variant="outline" :loading="loading" @click="handleExport">
        Daten exportieren
      </Button>
    </CardContent>
  </Card>
</template>
