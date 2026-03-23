<script setup lang="ts">
import { ref, watch } from 'vue'
import { useCookieConsent, type CookiePreferences } from '@/composables/useCookieConsent'
import { Cookie, Shield, BarChart3, Megaphone, MonitorPlay } from 'lucide-vue-next'
import Dialog from '@/components/ui/Dialog.vue'
import Switch from '@/components/ui/Switch.vue'
import Button from '@/components/ui/Button.vue'

defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { preferences, savePreferences } = useCookieConsent()

const local = ref<CookiePreferences>({
  necessary: true,
  statistics: preferences.value?.statistics ?? false,
  marketing: preferences.value?.marketing ?? false,
  external_media: preferences.value?.external_media ?? false,
})

// Sync local state when dialog opens
watch(() => preferences.value, (p) => {
  if (p) {
    local.value = { ...p }
  }
})

const categories = [
  {
    key: 'necessary' as const,
    icon: Shield,
    label: 'Notwendig',
    description: 'Erforderlich fur grundlegende Funktionen wie Anmeldung und Sicherheit.',
    locked: true,
    accent: 'text-emerald-400',
    glow: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
  },
  {
    key: 'statistics' as const,
    icon: BarChart3,
    label: 'Statistik',
    description: 'Anonyme Nutzungsstatistiken zur Verbesserung unserer Website.',
    locked: false,
    accent: 'text-blue-400',
    glow: 'bg-blue-500/10',
    border: 'border-blue-500/20',
  },
  {
    key: 'marketing' as const,
    icon: Megaphone,
    label: 'Marketing',
    description: 'Personalisierte Werbung und Remarketing-Funktionen.',
    locked: false,
    accent: 'text-amber-400',
    glow: 'bg-amber-500/10',
    border: 'border-amber-500/20',
  },
  {
    key: 'external_media' as const,
    icon: MonitorPlay,
    label: 'Externe Medien',
    description: 'Eingebettete Inhalte von Drittanbietern wie YouTube oder Google Maps.',
    locked: false,
    accent: 'text-violet-400',
    glow: 'bg-violet-500/10',
    border: 'border-violet-500/20',
  },
]

function save() {
  savePreferences({ ...local.value })
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" class="max-w-lg" @update:open="emit('update:open', $event)">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-5">
      <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20">
        <Cookie class="h-5 w-5 text-indigo-400" />
      </div>
      <div>
        <h2 class="font-mono text-lg font-semibold text-foreground">Cookie-Einstellungen</h2>
        <p class="text-xs text-zinc-500">Granulare Kontrolle uber Ihre Praferenzen</p>
      </div>
    </div>

    <p class="text-sm text-zinc-400 mb-6 leading-relaxed">
      Hier konnen Sie Ihre Cookie-Praferenzen einstellen.
      Notwendige Cookies konnen nicht deaktiviert werden, da sie fur den Betrieb der Website erforderlich sind.
    </p>

    <!-- Cookie categories -->
    <div class="space-y-3">
      <div
        v-for="cat in categories"
        :key="cat.key"
        :class="[
          'flex items-center justify-between rounded-xl border p-4 transition-colors',
          cat.locked ? 'border-emerald-500/10 bg-emerald-500/5' : 'border-white/[0.06] hover:border-white/[0.1] hover:bg-white/[0.02]',
        ]"
      >
        <div class="flex items-center gap-3">
          <div :class="['flex h-9 w-9 items-center justify-center rounded-lg border shrink-0', cat.glow, cat.border]">
            <component :is="cat.icon" :class="['h-4.5 w-4.5', cat.accent]" />
          </div>
          <div>
            <p class="text-sm font-medium text-foreground">{{ cat.label }}</p>
            <p class="text-xs text-zinc-500 mt-0.5 leading-relaxed">{{ cat.description }}</p>
          </div>
        </div>
        <Switch
          v-if="cat.locked"
          :model-value="true"
          disabled
          class="shrink-0 ml-4"
        />
        <Switch
          v-else
          v-model="local[cat.key]"
          class="shrink-0 ml-4"
        />
      </div>
    </div>

    <!-- Actions -->
    <div class="mt-6 flex justify-end gap-3">
      <Button variant="outline" @click="emit('update:open', false)">Abbrechen</Button>
      <Button @click="save" class="glow-sm">
        Einstellungen speichern
      </Button>
    </div>
  </Dialog>
</template>
