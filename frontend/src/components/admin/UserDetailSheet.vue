<script setup lang="ts">
import { formatDateShortDE, formatRelativeDE } from '@/lib/formatters'
import { X, Shield, ShieldOff, UserX, Mail, Phone, MapPin, Calendar } from 'lucide-vue-next'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Sheet from '@/components/ui/Sheet.vue'
import type { AdminUser } from '@/api/admin'

const props = defineProps<{
  open: boolean
  user: AdminUser | null
}>()

const emit = defineEmits<{
  close: []
  'toggle-active': [id: string]
  'toggle-staff': [id: string]
}>()
</script>

<template>
  <Sheet :open="open" side="right" class="w-96" @update:open="emit('close')">
    <div v-if="user" class="h-full flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-foreground">Benutzer-Details</h2>
        <button class="p-1 rounded-lg hover:bg-white/5" @click="emit('close')">
          <X class="h-5 w-5 text-zinc-500" />
        </button>
      </div>

      <!-- Avatar + Name -->
      <div class="flex items-center gap-4 mb-6">
        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700 text-lg font-mono font-bold text-zinc-300">
          {{ (user.first_name?.[0] || '') + (user.last_name?.[0] || '') || '?' }}
        </div>
        <div>
          <h3 class="text-base font-semibold text-foreground">{{ user.first_name }} {{ user.last_name }}</h3>
          <p class="text-sm font-mono text-zinc-500">{{ user.email }}</p>
        </div>
      </div>

      <!-- Status Badges -->
      <div class="flex flex-wrap gap-2 mb-6">
        <Badge :class="user.is_active ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'">
          {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
        </Badge>
        <Badge v-if="user.is_staff" class="bg-violet-500/10 text-violet-400 border-violet-500/20">
          Staff
        </Badge>
        <Badge v-if="user.is_email_verified" class="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
          E-Mail bestätigt
        </Badge>
        <Badge v-else class="bg-amber-500/10 text-amber-400 border-amber-500/20">
          E-Mail unbestätigt
        </Badge>
      </div>

      <!-- Info Grid -->
      <div class="space-y-3 mb-6 flex-1">
        <div class="flex items-center gap-3 text-sm">
          <Calendar class="h-4 w-4 text-zinc-600 shrink-0" />
          <span class="text-zinc-500">Registriert:</span>
          <span class="text-foreground font-mono text-xs">{{ formatDateShortDE(user.date_joined) }}</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <Calendar class="h-4 w-4 text-zinc-600 shrink-0" />
          <span class="text-zinc-500">Letzter Login:</span>
          <span class="text-foreground font-mono text-xs">{{ user.last_login ? formatRelativeDE(user.last_login) : '—' }}</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="text-zinc-500 ml-7">Tarif:</span>
          <span class="text-foreground font-mono text-xs">{{ user.subscription_plan }}</span>
        </div>
        <div class="flex items-center gap-3 text-sm">
          <span class="text-zinc-500 ml-7">Dokumente:</span>
          <span class="text-foreground font-mono text-xs">{{ user.document_count }}</span>
        </div>

        <!-- Profile details if available -->
        <template v-if="user.profile">
          <div class="border-t border-white/[0.04] pt-3 mt-3">
            <p class="text-[10px] font-mono text-zinc-600 uppercase tracking-wider mb-2">Profil</p>
          </div>
          <div v-if="user.profile.telefon" class="flex items-center gap-3 text-sm">
            <Phone class="h-4 w-4 text-zinc-600 shrink-0" />
            <span class="text-foreground font-mono text-xs">{{ user.profile.telefon }}</span>
          </div>
          <div v-if="user.profile.stadt || user.profile.plz" class="flex items-center gap-3 text-sm">
            <MapPin class="h-4 w-4 text-zinc-600 shrink-0" />
            <span class="text-foreground font-mono text-xs">{{ user.profile.plz }} {{ user.profile.stadt }}</span>
          </div>
        </template>
      </div>

      <!-- Actions -->
      <div class="space-y-2 border-t border-white/[0.04] pt-4">
        <Button
          class="w-full justify-start gap-2"
          variant="ghost"
          @click="emit('toggle-active', user.id)"
        >
          <UserX class="h-4 w-4" />
          {{ user.is_active ? 'Deaktivieren' : 'Aktivieren' }}
        </Button>
        <Button
          class="w-full justify-start gap-2"
          variant="ghost"
          @click="emit('toggle-staff', user.id)"
        >
          <component :is="user.is_staff ? ShieldOff : Shield" class="h-4 w-4" />
          {{ user.is_staff ? 'Staff entfernen' : 'Staff erteilen' }}
        </Button>
      </div>
    </div>
  </Sheet>
</template>
