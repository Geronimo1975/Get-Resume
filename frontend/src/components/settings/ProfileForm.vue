<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Anrede } from '@/types'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { ANREDE_OPTIONS } from '@/lib/constants'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'

const auth = useAuthStore()
const { toast } = useToast()

const form = ref({
  anrede: '',
  geburtsdatum: '',
  telefon: '',
})
const saving = ref(false)

onMounted(() => {
  const p = auth.user?.profile
  if (p) {
    form.value = {
      anrede: p.anrede || '',
      geburtsdatum: p.geburtsdatum || '',
      telefon: p.telefon || '',
    }
  }
})

async function save() {
  saving.value = true
  try {
    await auth.updateProfile({ ...form.value, anrede: form.value.anrede as Anrede })
    toast({ title: 'Gespeichert', description: 'Profil wurde aktualisiert.', variant: 'success' })
  } catch {
    toast({ title: 'Fehler', description: 'Profil konnte nicht gespeichert werden.', variant: 'destructive' })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Personliche Daten</h3>
      <p class="text-sm text-muted-foreground">Verwalten Sie Ihre personlichen Informationen</p>
    </CardHeader>
    <CardContent>
      <form class="space-y-4" @submit.prevent="save">
        <Select :model-value="form.anrede" :options="(ANREDE_OPTIONS as { value: string; label: string }[])" label="Anrede" @update:model-value="form.anrede = $event" />
        <Input v-model="form.geburtsdatum" label="Geburtsdatum" type="date" />
        <Input v-model="form.telefon" label="Telefon" type="tel" />
        <Button type="submit" :loading="saving">Speichern</Button>
      </form>
    </CardContent>
  </Card>
</template>
