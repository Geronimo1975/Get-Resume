import { useEditorStore } from '@/stores/editor'
import { createSection as apiCreateSection, deleteSection as apiDeleteSection, reorderSections as apiReorder } from '@/api/sections'
import { useToast } from '@/composables/useToast'
import type { SectionType } from '@/types'
import { SECTION_TYPES } from '@/lib/constants'

export function useSections() {
  const editor = useEditorStore()
  const { toast } = useToast()

  async function addSection(sectionType: SectionType) {
    if (!editor.document) return

    const typeInfo = SECTION_TYPES.find((t) => t.value === sectionType)
    const title = typeInfo?.label ?? sectionType
    const ordering = editor.document.sections.length

    try {
      const { data } = await apiCreateSection(editor.document.id, {
        section_type: sectionType,
        title,
        content: {},
        ordering,
      })
      editor.addSection(data)
    } catch {
      toast({ title: 'Fehler', description: 'Abschnitt konnte nicht hinzugefugt werden.', variant: 'destructive' })
    }
  }

  async function removeSection(sectionId: string) {
    if (!editor.document) return

    try {
      await apiDeleteSection(editor.document.id, sectionId)
      editor.removeSection(sectionId)
    } catch {
      toast({ title: 'Fehler', description: 'Abschnitt konnte nicht geloscht werden.', variant: 'destructive' })
    }
  }

  async function reorder(newOrder: string[]) {
    if (!editor.document) return

    editor.reorderSections(newOrder)
    try {
      await apiReorder(
        editor.document.id,
        newOrder.map((id, i) => ({ id, ordering: i }))
      )
    } catch {
      toast({ title: 'Fehler', description: 'Reihenfolge konnte nicht gespeichert werden.', variant: 'destructive' })
    }
  }

  return { addSection, removeSection, reorder }
}
