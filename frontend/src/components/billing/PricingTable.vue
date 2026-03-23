<script setup lang="ts">
import { SUBSCRIPTION_PLANS } from '@/lib/constants'
import PricingCard from './PricingCard.vue'

defineProps<{
  currentPlan?: string
}>()

defineEmits<{
  select: [planId: string]
}>()
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <PricingCard
      v-for="plan in SUBSCRIPTION_PLANS"
      :key="plan.id"
      :name="plan.name"
      :price="plan.price"
      :period="plan.period"
      :features="plan.features"
      :highlighted="plan.highlighted"
      :current="plan.id === currentPlan"
      @select="$emit('select', plan.id)"
    />
  </div>
</template>
