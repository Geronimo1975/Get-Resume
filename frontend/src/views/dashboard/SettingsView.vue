<script setup lang="ts">
import PageHeader from '@/components/shared/PageHeader.vue'
import ProfileForm from '@/components/settings/ProfileForm.vue'
import AddressForm from '@/components/settings/AddressForm.vue'
import LanguageSelector from '@/components/settings/LanguageSelector.vue'
import PrivacySettings from '@/components/settings/PrivacySettings.vue'
import GdprExportButton from '@/components/settings/GdprExportButton.vue'
import DeleteAccountDialog from '@/components/settings/DeleteAccountDialog.vue'
</script>

<template>
  <div>
    <PageHeader title="Einstellungen" description="Verwalten Sie Ihr Profil, Ihre Adresse und Datenschutzeinstellungen" />

    <div class="space-y-6 max-w-2xl">
      <ProfileForm />
      <AddressForm />
      <LanguageSelector />
      <PrivacySettings />
      <GdprExportButton />
      <DeleteAccountDialog />
    </div>
  </div>
</template>
