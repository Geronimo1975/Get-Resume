import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Document, Section } from '@/types'

export const useEditorStore = defineStore('editor', () => {
  const document = ref<Document | null>(null)
  const activeSectionId = ref<string | null>(null)
  const dirty = ref(false)
  const saving = ref(false)
  const saveError = ref<string | null>(null)
  const previewKey = ref(0)

  const activeSection = computed(() =>
    document.value?.sections.find((s) => s.id === activeSectionId.value) ?? null
  )

  const orderedSections = computed(() =>
    [...(document.value?.sections ?? [])].sort((a, b) => a.ordering - b.ordering)
  )

  const usedSectionTypes = computed(() =>
    new Set(document.value?.sections.map((s) => s.section_type) ?? [])
  )

  function setDocument(doc: Document) {
    document.value = doc
    dirty.value = false
    saving.value = false
    saveError.value = null
    // Auto-select first section
    if (doc.sections.length > 0) {
      const sorted = [...doc.sections].sort((a, b) => a.ordering - b.ordering)
      activeSectionId.value = sorted[0]?.id ?? null
    } else {
      activeSectionId.value = null
    }
  }

  function setActiveSection(sectionId: string) {
    activeSectionId.value = sectionId
  }

  function updateSectionContent(sectionId: string, content: Record<string, unknown>) {
    if (!document.value) return
    const section = document.value.sections.find((s) => s.id === sectionId)
    if (section) {
      section.content = content
      dirty.value = true
    }
  }

  function addSection(section: Section) {
    if (!document.value) return
    document.value.sections.push(section)
    activeSectionId.value = section.id
  }

  function removeSection(sectionId: string) {
    if (!document.value) return
    document.value.sections = document.value.sections.filter((s) => s.id !== sectionId)
    if (activeSectionId.value === sectionId) {
      activeSectionId.value = document.value.sections[0]?.id ?? null
    }
  }

  function reorderSections(newOrder: string[]) {
    if (!document.value) return
    document.value.sections = document.value.sections.map((s) => ({
      ...s,
      ordering: newOrder.indexOf(s.id),
    }))
    dirty.value = true
  }

  function toggleSectionVisibility(sectionId: string) {
    if (!document.value) return
    const section = document.value.sections.find((s) => s.id === sectionId)
    if (section) {
      section.is_visible = !section.is_visible
      dirty.value = true
    }
  }

  function markSaved() {
    dirty.value = false
    saving.value = false
    saveError.value = null
    previewKey.value++
  }

  function markSaving() {
    saving.value = true
    saveError.value = null
  }

  function markSaveError(error: string) {
    saving.value = false
    saveError.value = error
  }

  return {
    document,
    activeSectionId,
    dirty,
    saving,
    saveError,
    previewKey,
    activeSection,
    orderedSections,
    usedSectionTypes,
    setDocument,
    setActiveSection,
    updateSectionContent,
    addSection,
    removeSection,
    reorderSections,
    toggleSectionVisibility,
    markSaved,
    markSaving,
    markSaveError,
  }
})
