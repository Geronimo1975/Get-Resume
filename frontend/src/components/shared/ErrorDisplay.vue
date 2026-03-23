<script setup lang="ts">
import Button from '@/components/ui/Button.vue'

defineProps<{
  message?: string
}>()

defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div class="mb-4 rounded-xl bg-red-500/10 border border-red-500/20 p-4">
      <svg class="h-8 w-8 text-destructive" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 8v4M12 16h.01" />
      </svg>
    </div>
    <h3 class="text-lg font-semibold text-foreground">Etwas ist schiefgelaufen</h3>
    <p class="mt-1 max-w-sm text-sm text-muted-foreground">
      {{ message || 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut.' }}
    </p>
    <Button variant="outline" class="mt-4" @click="$emit('retry')">
      Erneut versuchen
    </Button>
  </div>
</template>
