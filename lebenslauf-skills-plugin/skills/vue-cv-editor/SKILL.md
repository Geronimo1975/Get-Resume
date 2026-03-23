---
name: vue-cv-editor
description: >
  This skill should be used when the user asks to "build the CV editor", "create editor components",
  "implement live preview", "add drag and drop sections", "build the photo upload",
  "implement template switching", "create dynamic forms", "build the Bewerbungsmappe builder",
  "implement autosave", or mentions editor UI, Vue.js editor, live preview, dynamic forms,
  section management, photo upload, template switching, drag and drop, CV editor,
  split pane layout, autosave, Pinia editor store, or any editor-related frontend work.
  Triggers on: editor, CV editor, Lebenslauf editor, drag and drop, live preview,
  photo upload, section form, template selector, theme picker, autosave, Bewerbungsmappe.
---

# Vue.js CV Editor

Vue.js 3 SPA-based CV editor for the GetResume platform with drag-and-drop sections, live HTML preview, autosave, and PDF export.

## Architecture

- **Vue.js 3** with Composition API + TypeScript
- **Pinia** store for editor state (active document, sections, undo/redo history)
- **vue-draggable-plus** for drag & drop section reordering
- **Cropper.js** for photo upload + crop
- **Axios** for API communication with Django DRF backend
- **Split pane** layout: section sidebar | edit form | live preview
- **WeasyPrint** on server for PDF generation (triggered via API)

## Editor Layout

```
┌──────────────────────────────────────────────────────┐
│  Toolbar: [Template ▼] [Theme ▼] [⟳ Undo] [↻ Redo]  │
│           [📥 PDF Download] [ATS Score: 85]          │
├──────────┬────────────────────┬──────────────────────┤
│ Sections │   Edit Form        │   Live Preview       │
│ sidebar  │   (Vue components) │   (iframe / shadow)  │
│          │                    │                      │
│ ≡ Pers.  │   <SectionForm     │   Rendered HTML      │
│ ≡ Beruf  │    :section="..."  │   from API           │
│ ≡ Ausbil │    @save="patch"   │                      │
│ ≡ Kennt  │   />               │                      │
│          │                    │                      │
│ [+ Add]  │                    │                      │
└──────────┴────────────────────┴──────────────────────┘
```

## Key Vue Components

```
src/components/editor/
├── EditorLayout.vue          # Main split-pane layout
├── SectionSidebar.vue        # Draggable section list
├── SectionForm.vue           # Dynamic form by section type
├── sections/                 # Section-specific forms
│   ├── PersoenlicheDaten.vue # Personal data + photo
│   ├── Berufserfahrung.vue   # Work experience (repeatable)
│   ├── Ausbildung.vue        # Education (repeatable)
│   ├── Kenntnisse.vue        # Skills with rating bars
│   ├── Sprachen.vue          # Languages with CEFR levels
│   ├── Weiterbildungen.vue   # Certifications
│   ├── Ehrenamt.vue          # Volunteer work
│   ├── Interessen.vue        # Hobbies/interests
│   └── Unterschrift.vue      # Signature line (Ort + Datum)
├── PhotoUpload.vue           # Drag & drop + crop
├── SkillRating.vue           # Skill bar component (5 levels)
├── LanguageLevel.vue         # CEFR level selector (A1–C2)
├── LivePreview.vue           # iframe showing rendered CV HTML
├── TemplateSelector.vue      # Template grid with thumbnails
├── ThemePicker.vue           # Color theme + font picker
├── ToolbarActions.vue        # Download, undo/redo, ATS score
└── BewerbungsmappeBuilder.vue # Combine documents into package
```

## Pinia Editor Store

```typescript
// stores/editor.ts
interface EditorState {
  document: Document | null
  sections: Section[]
  activeSection: string | null
  template: Template
  theme: Theme
  isDirty: boolean
  isSaving: boolean
  atsScore: number | null
  undoStack: Snapshot[]
  redoStack: Snapshot[]
}

// Key actions:
// - loadDocument(id): GET /api/v1/documents/{id}/
// - saveDocument(): PATCH /api/v1/documents/{id}/ (debounced 2s)
// - addSection(type): append to sections array
// - removeSection(id): remove + confirm modal
// - reorderSections(newOrder): update sort_order via API
// - changeTemplate(id): GET /api/v1/templates/{id}/ + refresh preview
// - changeTheme(id): update theme + refresh preview
// - refreshPreview(): GET /api/v1/documents/{id}/preview/
// - downloadPdf(): GET /api/v1/documents/{id}/pdf/
// - getAtsScore(): GET /api/v1/documents/{id}/ats-score/
// - undo() / redo(): restore from snapshot stack
```

## Autosave Flow

```
User edits field
  → Pinia store updates (reactive)
  → useDebounce(2000ms)
  → PATCH /api/v1/documents/{id}/ with { content: JSON }
  → Show "Gespeichert" indicator
  → Refresh preview iframe
```

## Photo Upload

- Drag & drop zone with progress bar
- Client-side crop via Cropper.js (aspect ratio for CV photo)
- POST /api/v1/users/me/photo/ (multipart/form-data)
- Server-side resize + optimization (Pillow)
- Max file size: 5MB, accepted: JPEG, PNG, WebP

## Live Preview

- Separate iframe or shadow DOM in right panel
- API call: `GET /api/v1/documents/{id}/preview/` returns rendered HTML
- Refreshed on every content change (debounced)
- Template/theme changes trigger full preview reload
- PDF generation only on explicit "Download" click

## German CV Sections

| Section | Features |
|---------|----------|
| Persönliche Daten | Photo, Geburtsdatum, Familienstand, Staatsangehörigkeit |
| Berufserfahrung | Sortable, repeatable, date range picker, description |
| Ausbildung | Sortable, repeatable, degree type selector |
| Kenntnisse | Skill bars: Grundkenntnisse → Experte (5 levels) |
| Sprachen | CEFR A1–C2 dropdown + Muttersprache toggle |
| Weiterbildungen | Date, title, provider fields |
| Ehrenamt | Date range, organization, role |
| Interessen | Tag-style chip input |
| Unterschrift | Ort text + Datum auto-filled |

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/documents/` | POST | Create new document |
| `/api/v1/documents/{id}/` | GET | Load document content |
| `/api/v1/documents/{id}/` | PATCH | Autosave content |
| `/api/v1/documents/{id}/preview/` | GET | HTML preview |
| `/api/v1/documents/{id}/pdf/` | GET | Download PDF |
| `/api/v1/documents/{id}/ats-score/` | GET | ATS analysis |
| `/api/v1/templates/` | GET | Template catalog |
| `/api/v1/themes/` | GET | Available themes |
| `/api/v1/users/me/photo/` | POST | Upload photo |

## Additional Resources

### Reference Files

For detailed component implementations and patterns:
- **`references/editor-templates.md`** — Vue component patterns, CSS structure
- **`references/editor-views.md`** — Django DRF views for editor API endpoints
