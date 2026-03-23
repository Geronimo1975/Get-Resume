<script setup lang="ts">
import { useEditorStore } from '@/stores/editor'
import SectionList from './SectionList.vue'
import LivePreview from './LivePreview.vue'
import ScrollArea from '@/components/ui/ScrollArea.vue'
import type { SectionType } from '@/types'

// Section forms
import PersoenlicheDatenForm from './forms/PersoenlicheDatenForm.vue'
import BerufserfahrungForm from './forms/BerufserfahrungForm.vue'
import AusbildungForm from './forms/AusbildungForm.vue'
import KenntnisseForm from './forms/KenntnisseForm.vue'
import SprachenForm from './forms/SprachenForm.vue'
import WeiterbildungenForm from './forms/WeiterbildungenForm.vue'
import EhrenamtForm from './forms/EhrenamtForm.vue'
import InteressenForm from './forms/InteressenForm.vue'
import UnterschriftForm from './forms/UnterschriftForm.vue'

const editor = useEditorStore()

defineEmits<{
  addSection: [type: SectionType]
  removeSection: [id: string]
}>()

const formComponents: Record<string, unknown> = {
  persoenliche_daten: PersoenlicheDatenForm,
  berufserfahrung: BerufserfahrungForm,
  ausbildung: AusbildungForm,
  kenntnisse: KenntnisseForm,
  sprachen: SprachenForm,
  weiterbildungen: WeiterbildungenForm,
  ehrenamt: EhrenamtForm,
  interessen: InteressenForm,
  unterschrift: UnterschriftForm,
}

function handleSectionUpdate(content: Record<string, unknown>) {
  if (!editor.activeSection) return
  editor.updateSectionContent(editor.activeSection.id, content)
}
</script>

<template>
  <div class="flex h-full">
    <!-- Section sidebar -->
    <div class="w-48 shrink-0">
      <SectionList
        @add-section="$emit('addSection', $event)"
        @remove-section="$emit('removeSection', $event)"
      />
    </div>

    <!-- Edit form -->
    <div class="flex-1 border-r border-white/[0.06]">
      <ScrollArea class="h-full p-4">
        <template v-if="editor.activeSection">
          <h3 class="mb-4 text-lg font-mono font-semibold text-foreground">
            {{ editor.activeSection.title }}
          </h3>
          <component
            :is="formComponents[editor.activeSection.section_type]"
            :content="editor.activeSection.content"
            @update="handleSectionUpdate"
          />
        </template>
        <div v-else class="flex h-full items-center justify-center text-muted-foreground">
          <p class="text-sm">Wahlen Sie einen Abschnitt aus oder fugen Sie einen neuen hinzu.</p>
        </div>
      </ScrollArea>
    </div>

    <!-- Live preview -->
    <div class="hidden lg:block flex-1">
      <LivePreview />
    </div>
  </div>
</template>
