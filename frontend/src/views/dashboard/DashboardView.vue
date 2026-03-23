<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDocumentsStore } from '@/stores/documents'
import { formatRelativeDE } from '@/lib/formatters'
import { FileText, Plus, CreditCard, TrendingUp, ArrowRight, Sparkles, Clock } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Skeleton from '@/components/ui/Skeleton.vue'
import EmptyState from '@/components/shared/EmptyState.vue'
import PageHeader from '@/components/shared/PageHeader.vue'

const auth = useAuthStore()
const docs = useDocumentsStore()
const router = useRouter()

onMounted(() => {
  docs.fetchDocuments()
})

function goToNewDoc() {
  router.push('/app/documents?create=true')
}
</script>

<template>
  <div>
    <PageHeader
      :title="`Willkommen zuruck, ${auth.user?.first_name || 'Nutzer'}`"
      description="Ihr Bewerbungs-Dashboard auf einen Blick"
      title-class="font-mono"
    >
      <template #actions>
        <Button
          @click="goToNewDoc"
          class="bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all"
        >
          <Plus class="h-4 w-4" />
          Neuer Lebenslauf
        </Button>
      </template>
    </PageHeader>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">

      <!-- Documents count -->
      <Card class="group relative overflow-hidden bg-card border-border hover:glow-border hover:-translate-y-0.5 transition-all duration-300">
        <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <CardContent class="relative pt-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-zinc-400">Dokumente</p>
              <p class="mt-1 text-3xl font-mono font-bold text-foreground">{{ docs.documents.length }}</p>
            </div>
            <div class="flex h-14 w-14 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20 shrink-0">
              <FileText class="h-6 w-6 text-indigo-400" />
            </div>
          </div>
          <div class="mt-3 flex items-center gap-1.5 text-xs text-zinc-500">
            <TrendingUp class="h-3.5 w-3.5 text-emerald-500" />
            <span class="text-emerald-500 font-medium font-mono">Aktiv</span>
          </div>
        </CardContent>
      </Card>

      <!-- Subscription -->
      <Card class="group relative overflow-hidden bg-card border-border hover:glow-border hover:-translate-y-0.5 transition-all duration-300">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <CardContent class="relative pt-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-zinc-400">Abonnement</p>
              <div class="mt-1.5">
                <Badge :variant="auth.isPremium ? 'premium' : 'secondary'" class="text-sm px-3 py-1">
                  {{ auth.isPremium ? 'Premium' : 'Kostenlos' }}
                </Badge>
              </div>
            </div>
            <div class="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20 shrink-0">
              <CreditCard class="h-6 w-6 text-emerald-400" />
            </div>
          </div>
          <div v-if="!auth.isPremium" class="mt-3">
            <RouterLink
              to="/app/billing"
              class="text-xs font-mono font-medium text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 transition-colors"
            >
              Upgrade auf Premium
              <ArrowRight class="h-3 w-3" />
            </RouterLink>
          </div>
        </CardContent>
      </Card>

      <!-- Quick start CTA -->
      <Card class="relative overflow-hidden border-0 group">
        <!-- Dark gradient background: indigo-950 to violet-950 -->
        <div class="absolute inset-0 bg-gradient-to-br from-indigo-950 via-indigo-950 to-violet-950"></div>
        <!-- Grid overlay -->
        <div class="absolute inset-0 bg-grid opacity-30"></div>
        <!-- Ambient glow orbs -->
        <div class="absolute -top-10 -right-10 h-28 w-28 rounded-full bg-indigo-500/15 blur-2xl"></div>
        <div class="absolute -bottom-6 -left-6 h-20 w-20 rounded-full bg-violet-500/15 blur-2xl"></div>

        <CardContent class="relative pt-6">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <Sparkles class="h-4 w-4 text-indigo-400" />
                <p class="text-sm font-mono font-semibold text-indigo-300">Schnellstart</p>
              </div>
              <p class="text-sm text-zinc-400 leading-relaxed">
                Erstellen Sie jetzt Ihren professionellen Lebenslauf.
              </p>
            </div>
          </div>
          <Button
            size="sm"
            class="mt-4 bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-500/30 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all font-mono"
            @click="goToNewDoc"
          >
            <Plus class="h-4 w-4" />
            Neuer Lebenslauf
          </Button>
        </CardContent>
      </Card>
    </div>

    <!-- Recent Documents -->
    <Card class="border-border overflow-hidden bg-card">
      <div class="flex items-center justify-between p-6 pb-0">
        <div class="flex items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20">
            <Clock class="h-4 w-4 text-indigo-400" />
          </div>
          <h2 class="text-base font-mono font-semibold text-foreground">Letzte Dokumente</h2>
        </div>
        <RouterLink
          v-if="docs.documents.length > 0"
          to="/app/documents"
          class="text-xs font-mono font-medium text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 transition-colors"
        >
          Alle anzeigen
          <ArrowRight class="h-3.5 w-3.5" />
        </RouterLink>
      </div>

      <CardContent class="pt-4">
        <!-- Loading -->
        <div v-if="docs.loading" class="space-y-3">
          <Skeleton v-for="i in 3" :key="i" class="h-18 w-full rounded-xl" />
        </div>

        <!-- Empty -->
        <EmptyState
          v-else-if="docs.documents.length === 0"
          title="Keine Dokumente"
          description="Erstellen Sie Ihren ersten Lebenslauf, um loszulegen."
          action-label="Neuer Lebenslauf"
          @action="goToNewDoc"
        />

        <!-- Documents list -->
        <div v-else class="space-y-1">
          <RouterLink
            v-for="doc in docs.documents.slice(0, 5)"
            :key="doc.id"
            :to="`/editor/${doc.id}`"
            class="group flex items-center justify-between py-3.5 px-4 -mx-2 rounded-xl hover:bg-white/[0.03] transition-all duration-200"
          >
            <div class="flex items-center gap-4">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 shrink-0 group-hover:bg-indigo-500/15 transition-colors">
                <FileText class="h-4 w-4 text-indigo-400" />
              </div>
              <div>
                <p class="font-medium text-foreground group-hover:text-indigo-300 transition-colors text-sm">{{ doc.title }}</p>
                <p class="text-xs font-mono text-zinc-500 mt-0.5">{{ formatRelativeDE(doc.updated_at) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <Badge variant="secondary" class="text-xs font-mono bg-zinc-800 text-zinc-400 border-zinc-700">
                {{ doc.doc_type }}
              </Badge>
              <ArrowRight class="h-4 w-4 text-transparent group-hover:text-indigo-500 transition-all" />
            </div>
          </RouterLink>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
