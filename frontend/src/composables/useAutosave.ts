import { watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { useEditorStore } from '@/stores/editor'
import { updateDocument } from '@/api/documents'
import { updateSection } from '@/api/sections'

export function useAutosave() {
  const editor = useEditorStore()

  const debouncedSave = useDebounceFn(async () => {
    if (!editor.document || !editor.dirty) return

    editor.markSaving()
    try {
      // Save all sections that have changed
      for (const section of editor.document.sections) {
        await updateSection(editor.document.id, section.id, {
          content: section.content,
          is_visible: section.is_visible,
          ordering: section.ordering,
        })
      }

      // Save document-level changes
      await updateDocument(editor.document.id, {
        title: editor.document.title,
        theme: editor.document.theme,
      })

      editor.markSaved()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Speichern fehlgeschlagen'
      editor.markSaveError(message)
    }
  }, 2000)

  // Watch for dirty state changes
  watch(() => editor.dirty, (isDirty) => {
    if (isDirty) debouncedSave()
  })

  return { save: debouncedSave }
}
