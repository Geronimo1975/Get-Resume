<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Bundesland } from '@/types'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import BundeslandSelect from '@/components/shared/BundeslandSelect.vue'

const auth = useAuthStore()
const { toast } = useToast()

const form = ref({
  strasse: '',
  plz: '',
  stadt: '',
  bundesland: '',
})
const saving = ref(false)

onMounted(() => {
  const p = auth.user?.profile
  if (p) {
    form.value = {
      strasse: p.strasse || '',
      plz: p.plz || '',
      stadt: p.stadt || '',
      bundesland: p.bundesland || '',
    }
  }
})

async function save() {
  saving.value = true
  try {
    await auth.updateProfile({ ...form.value, bundesland: form.value.bundesland as Bundesland })
    toast({ title: 'Gespeichert', description: 'Adresse wurde aktualisiert.', variant: 'success' })
  } catch {
    toast({ title: 'Fehler', description: 'Adresse konnte nicht gespeichert werden.', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Adresse</h3>
      <p class="text-sm text-muted-foreground">Ihre Postanschrift</p>
    </CardHeader>
    <CardContent>
      <form class="space-y-4" @submit.prevent="save">
        <Input v-model="form.strasse" label="Strafle und Hausnummer" />
        <div class="grid grid-cols-3 gap-4">
          <Input v-model="form.plz" label="PLZ" maxlength="5" />
          <Input v-model="form.stadt" label="Stadt" class="col-span-2" />
        </div>
        <BundeslandSelect v-model="form.bundesland" />
        <Button type="submit" :loading="saving">Speichern</Button>
      </form>
    </CardContent>
  </Card>
</template>
