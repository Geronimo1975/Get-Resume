<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchInvoices } from '@/api/payments'
import { formatDateShortDE } from '@/lib/formatters'
import type { Invoice } from '@/types'
import { Download } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Skeleton from '@/components/ui/Skeleton.vue'

const invoices = ref<Invoice[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await fetchInvoices()
    invoices.value = data
  } catch {
    // Silent — invoices may not be available yet
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <Card>
    <CardHeader>
      <h3 class="text-lg font-semibold">Rechnungen</h3>
    </CardHeader>
    <CardContent>
      <div v-if="loading" class="space-y-3">
        <Skeleton v-for="i in 3" :key="i" class="h-12 w-full" />
      </div>

      <p v-else-if="invoices.length === 0" class="text-sm text-muted-foreground">
        Noch keine Rechnungen vorhanden.
      </p>

      <div v-else class="divide-y divide-border">
        <div
          v-for="invoice in invoices"
          :key="invoice.id"
          class="flex items-center justify-between py-3"
        >
          <div>
            <p class="text-sm font-medium text-foreground">{{ invoice.rechnungsnummer }}</p>
            <p class="text-xs text-muted-foreground">{{ formatDateShortDE(invoice.datum) }}</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm font-medium text-foreground">{{ invoice.betrag }}</span>
            <a
              v-if="invoice.pdf_url"
              :href="invoice.pdf_url"
              class="rounded-md p-1 hover:bg-accent transition-colors"
              target="_blank"
            >
              <Download class="h-4 w-4 text-muted-foreground" />
            </a>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
