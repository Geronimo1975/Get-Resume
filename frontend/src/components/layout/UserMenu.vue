<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Avatar from '@/components/ui/Avatar.vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue'
import Separator from '@/components/ui/Separator.vue'
import SubscriptionBadge from './SubscriptionBadge.vue'

const auth = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <DropdownMenu>
    <template #trigger>
      <button class="flex items-center gap-2 rounded-lg p-1.5 hover:bg-accent transition-colors">
        <Avatar :fallback="auth.userInitials" size="sm" />
        <span class="hidden md:block text-sm font-medium text-foreground">
          {{ auth.user?.first_name }}
        </span>
      </button>
    </template>

    <div class="px-2 py-1.5">
      <p class="text-sm font-medium">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</p>
      <p class="text-xs text-muted-foreground">{{ auth.user?.email }}</p>
      <SubscriptionBadge class="mt-1" />
    </div>

    <Separator class="my-1" />

    <DropdownMenuItem @click="router.push('/app/settings')">
      Profil & Einstellungen
    </DropdownMenuItem>
    <DropdownMenuItem @click="router.push('/app/billing')">
      Abonnement
    </DropdownMenuItem>

    <Separator class="my-1" />

    <DropdownMenuItem destructive @click="handleLogout">
      Abmelden
    </DropdownMenuItem>
  </DropdownMenu>
</template>
