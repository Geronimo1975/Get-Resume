# Editor Templates Reference

HTMX/Alpine.js template patterns for the CV editor interface.

---

## 1. editor_base.html (3-Column Layout)

```html
{# templates/editor/editor_base.html #}

{% extends "base.html" %}
{% load static %}

{% block title %}{{ document.title }} bearbeiten | Lebenslauf-Builder{% endblock %}

{% block extra_head %}
{# Cropper.js for photo crop #}
<link rel="stylesheet" href="{% static 'vendor/cropper/cropper.min.css' %}">
{% endblock %}

{% block content %}
<div x-data="editorApp()" class="h-screen flex flex-col bg-gray-100">

  {# ── Toolbar ───────────────────────────────────── #}
  <header class="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between flex-shrink-0">
    <div class="flex items-center gap-4">
      {# Back to dashboard #}
      <a href="{% url 'dashboard:index' %}"
         class="text-gray-500 hover:text-gray-700 transition"
         title="Zurück zum Dashboard">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
      </a>

      {# Document title (inline editable) #}
      <input type="text"
             value="{{ document.title }}"
             class="text-lg font-semibold border-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
             hx-put="{% url 'editor:section_update' section_id=active_section.id %}"
             hx-trigger="change"
             hx-swap="none"
             name="title">
    </div>

    <div class="flex items-center gap-3">
      {# Save indicator #}
      <span id="save-indicator" class="htmx-indicator text-sm text-gray-400">
        Speichert...
      </span>
      <span id="save-status" class="text-sm text-green-600 hidden">
        Gespeichert
      </span>

      {# Template selector button #}
      <button type="button"
              hx-get="{% url 'editor:template_select' document_id=document.id %}"
              hx-target="#modal-container"
              hx-swap="innerHTML"
              class="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/>
        </svg>
        Vorlage
      </button>

      {# Download PDF #}
      <a href="{% url 'editor:document_download' document_id=document.id %}"
         class="px-4 py-1.5 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        PDF herunterladen
      </a>
    </div>
  </header>

  {# ── Three-Column Layout ───────────────────────── #}
  <div class="flex-1 flex overflow-hidden">

    {# ── Left: Section Sidebar ─────────────────── #}
    <aside id="section-sidebar"
           class="w-56 bg-white border-r border-gray-200 flex flex-col flex-shrink-0">
      <div class="p-3 border-b border-gray-100">
        <h2 class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Abschnitte</h2>
      </div>

      {# Sortable section list #}
      <div id="section-list"
           class="flex-1 overflow-y-auto p-2 space-y-1"
           x-ref="sectionList"
           x-init="initSortable($refs.sectionList)">

        {% for section in sections %}
          <div class="section-item group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition
                      {% if section.id == active_section.id %}bg-blue-50 text-blue-700{% else %}hover:bg-gray-50{% endif %}"
               data-section-id="{{ section.id }}"
               hx-get="{% url 'editor:section_form' section_id=section.id %}"
               hx-target="#section-form-area"
               hx-swap="innerHTML"
               @click="activeSection = '{{ section.id }}'">

            {# Drag handle #}
            <span class="drag-handle cursor-grab text-gray-400 opacity-0 group-hover:opacity-100 transition">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M7 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/>
              </svg>
            </span>

            {# Section name #}
            <span class="flex-1 text-sm font-medium truncate">
              {{ section.get_section_type_display }}
            </span>

            {# Visibility toggle #}
            <button type="button"
                    @click.stop="toggleVisibility('{{ section.id }}')"
                    class="opacity-0 group-hover:opacity-100 transition text-gray-400 hover:text-gray-600"
                    title="{% if section.is_visible %}Ausblenden{% else %}Einblenden{% endif %}">
              {% if section.is_visible %}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
              {% else %}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              {% endif %}
            </button>
          </div>
        {% endfor %}
      </div>

      {# Add section dropdown #}
      {% if available_section_types %}
      <div class="p-3 border-t border-gray-100">
        <div x-data="{ open: false }" class="relative">
          <button @click="open = !open"
                  class="w-full px-3 py-2 text-sm bg-blue-50 text-blue-600 hover:bg-blue-100
                         rounded-lg transition flex items-center justify-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Abschnitt hinzufügen
          </button>
          <div x-show="open"
               @click.away="open = false"
               x-transition
               class="absolute bottom-full left-0 right-0 mb-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
            {% for value, label in available_section_types %}
              <button type="button"
                      hx-post="{% url 'editor:section_create' document_id=document.id %}"
                      hx-vals='{"section_type": "{{ value }}"}'
                      hx-target="#section-list"
                      hx-swap="beforeend"
                      @click="open = false"
                      class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition">
                {{ label }}
              </button>
            {% endfor %}
          </div>
        </div>
      </div>
      {% endif %}
    </aside>

    {# ── Center: Section Form ──────────────────── #}
    <main id="section-form-area"
          class="flex-1 overflow-y-auto p-6 bg-gray-50">
      {% if active_section %}
        {% include "editor/forms/"|add:active_section.section_type|add:".html" with section=active_section content=active_section.content document=document %}
      {% else %}
        <div class="flex items-center justify-center h-full text-gray-400">
          <p>Waehlen Sie einen Abschnitt aus der Seitenleiste</p>
        </div>
      {% endif %}
    </main>

    {# ── Right: Live Preview ───────────────────── #}
    <aside class="w-[420px] bg-gray-200 flex-shrink-0 flex flex-col border-l border-gray-300">
      <div class="p-2 bg-white border-b border-gray-200 flex items-center justify-between">
        <span class="text-xs font-medium text-gray-500 uppercase">Vorschau</span>
        <div class="flex gap-1">
          <button @click="previewScale = 0.5" :class="previewScale === 0.5 ? 'bg-gray-200' : ''"
                  class="px-2 py-0.5 text-xs rounded">50%</button>
          <button @click="previewScale = 0.75" :class="previewScale === 0.75 ? 'bg-gray-200' : ''"
                  class="px-2 py-0.5 text-xs rounded">75%</button>
          <button @click="previewScale = 1" :class="previewScale === 1 ? 'bg-gray-200' : ''"
                  class="px-2 py-0.5 text-xs rounded">100%</button>
        </div>
      </div>
      <div class="flex-1 overflow-auto p-4 flex justify-center">
        <div :style="{ transform: `scale(${previewScale})`, transformOrigin: 'top center' }">
          <iframe id="preview-iframe"
                  src="{% url 'editor:preview' document_id=document.id %}"
                  class="bg-white shadow-xl border border-gray-300"
                  style="width: 210mm; height: 297mm;"
                  hx-get="{% url 'editor:preview' document_id=document.id %}"
                  hx-trigger="preview-refresh from:body"
                  hx-target="this"
                  hx-swap="innerHTML"
                  sandbox="allow-same-origin">
          </iframe>
        </div>
      </div>
    </aside>

  </div>

</div>

{# Modal container (for template selector, etc.) #}
<div id="modal-container"></div>

{% endblock %}

{% block extra_scripts %}
{# Sortable.js for drag & drop #}
<script src="{% static 'vendor/sortablejs/Sortable.min.js' %}"></script>
{# Cropper.js for photo crop #}
<script src="{% static 'vendor/cropper/cropper.min.js' %}"></script>
{# Editor Alpine.js app #}
<script>
{% include "editor/js/editor_app.js" %}
</script>
{% endblock %}
```

---

## 2. section_form.html (HTMX Partial for Single Section)

### Berufserfahrung Form Example

```html
{# templates/editor/forms/berufserfahrung.html #}

<div class="max-w-2xl">
  <h2 class="text-xl font-semibold mb-4">Berufserfahrung</h2>

  <form hx-put="{% url 'editor:section_update' section_id=section.id %}"
        hx-trigger="keyup changed delay:500ms, change"
        hx-swap="none"
        hx-indicator="#save-indicator"
        id="form-{{ section.id }}">
    {% csrf_token %}

    <div id="entries-container" class="space-y-6">
      {% for eintrag in content.eintraege %}
        {% include "editor/forms/partials/berufserfahrung_entry.html" with entry=eintrag index=forloop.counter0 %}
      {% empty %}
        {# Empty state with first entry #}
        {% include "editor/forms/partials/berufserfahrung_entry.html" with entry=None index=0 %}
      {% endfor %}
    </div>

    {# Add entry button #}
    <button type="button"
            x-data
            @click="addBerufserfahrungEntry()"
            class="mt-4 w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg
                   text-gray-500 hover:border-blue-400 hover:text-blue-500 transition text-sm">
      + Weitere Berufserfahrung hinzufuegen
    </button>
  </form>
</div>
```

### Berufserfahrung Entry Partial

```html
{# templates/editor/forms/partials/berufserfahrung_entry.html #}

<div class="entry-card bg-white rounded-lg border border-gray-200 p-4"
     x-data="{ collapsed: false }"
     data-entry-index="{{ index }}">

  {# Entry header (collapsible) #}
  <div class="flex items-center justify-between cursor-pointer mb-3"
       @click="collapsed = !collapsed">
    <h3 class="font-medium text-sm">
      {{ entry.position|default:"Neue Berufserfahrung" }}
    </h3>
    <div class="flex items-center gap-2">
      {# Delete entry #}
      <button type="button"
              @click.stop="removeEntry($el.closest('.entry-card'))"
              class="text-gray-400 hover:text-red-500 transition"
              title="Eintrag entfernen">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
        </svg>
      </button>
      {# Collapse toggle #}
      <svg class="w-4 h-4 text-gray-400 transition-transform" :class="{ 'rotate-180': !collapsed }"
           fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </div>
  </div>

  {# Entry fields #}
  <div x-show="!collapsed" x-transition class="space-y-3">
    <input type="hidden" name="entry_{{ index }}_id" value="{{ entry.id|default:'' }}">

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Position / Jobtitel</label>
        <input type="text"
               name="entry_{{ index }}_position"
               value="{{ entry.position|default:'' }}"
               class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
               placeholder="z.B. Senior Softwareentwickler">
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Unternehmen</label>
        <input type="text"
               name="entry_{{ index }}_unternehmen"
               value="{{ entry.unternehmen|default:'' }}"
               class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
               placeholder="z.B. SAP SE">
      </div>
    </div>

    <div class="grid grid-cols-3 gap-3">
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Von</label>
        <input type="month"
               name="entry_{{ index }}_von"
               value="{{ entry.von|default:'' }}"
               class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
      </div>
      <div>
        <label class="block text-xs font-medium text-gray-600 mb-1">Bis</label>
        <input type="month"
               name="entry_{{ index }}_bis"
               value="{{ entry.bis|default:'' }}"
               class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
      </div>
      <div class="flex items-end pb-2">
        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox"
                 name="entry_{{ index }}_ist_aktuell"
                 {% if entry.ist_aktuell %}checked{% endif %}
                 class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
          <span class="text-sm text-gray-600">Bis heute</span>
        </label>
      </div>
    </div>

    <div>
      <label class="block text-xs font-medium text-gray-600 mb-1">Ort</label>
      <input type="text"
             name="entry_{{ index }}_ort"
             value="{{ entry.ort|default:'' }}"
             class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
             placeholder="z.B. Walldorf, Baden-Wuerttemberg">
    </div>

    <div>
      <label class="block text-xs font-medium text-gray-600 mb-1">Aufgaben und Erfolge</label>
      <textarea name="entry_{{ index }}_aufgaben"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                placeholder="Eine Aufgabe pro Zeile">{{ entry.aufgaben|join:"\n"|default:'' }}</textarea>
      <p class="text-xs text-gray-400 mt-1">Eine Aufgabe pro Zeile (wird als Aufzaehlungspunkte dargestellt)</p>
    </div>
  </div>
</div>
```

---

## 3. photo_upload.html (Drag & Drop with Cropper.js)

```html
{# templates/editor/forms/partials/photo_upload.html #}

<div x-data="photoUploader()" class="mb-6">
  <label class="block text-xs font-medium text-gray-600 mb-2">Bewerbungsfoto</label>

  {# Current photo preview #}
  <div id="photo-preview-container" class="mb-3">
    {% if content.foto %}
      <div class="relative inline-block">
        <img src="{{ content.foto }}"
             alt="Bewerbungsfoto"
             class="w-32 h-40 object-cover rounded-lg border border-gray-200">
        <button type="button"
                @click="removePhoto()"
                class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600">
          X
        </button>
      </div>
    {% endif %}
  </div>

  {# Drop zone #}
  <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center
              hover:border-blue-400 transition cursor-pointer"
       @dragover.prevent="isDragging = true"
       @dragleave.prevent="isDragging = false"
       @drop.prevent="handleDrop($event)"
       @click="$refs.fileInput.click()"
       :class="{ 'border-blue-400 bg-blue-50': isDragging }">

    <input type="file"
           x-ref="fileInput"
           @change="handleFileSelect($event)"
           accept="image/jpeg,image/png,image/webp"
           class="hidden">

    <svg class="mx-auto w-10 h-10 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
    </svg>
    <p class="text-sm text-gray-500">
      <span class="text-blue-600 font-medium">Foto hochladen</span>
      oder hierher ziehen
    </p>
    <p class="text-xs text-gray-400 mt-1">JPEG, PNG oder WebP (max. 5 MB)</p>
  </div>

  {# Crop modal #}
  <div x-show="showCropModal"
       x-transition
       class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
       @keyup.escape="cancelCrop()">
    <div class="bg-white rounded-xl shadow-2xl p-6 max-w-lg w-full mx-4" @click.stop>
      <h3 class="text-lg font-semibold mb-4">Foto zuschneiden</h3>
      <div class="max-h-96 overflow-hidden">
        <img x-ref="cropImage" :src="cropImageSrc" class="max-w-full">
      </div>
      <div class="flex justify-end gap-3 mt-4">
        <button type="button" @click="cancelCrop()"
                class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition">
          Abbrechen
        </button>
        <button type="button" @click="applyCrop()"
                class="px-4 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition">
          Zuschneiden & Hochladen
        </button>
      </div>
    </div>
  </div>

  {# Upload progress #}
  <div x-show="uploading" class="mt-3">
    <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
      <div class="h-full bg-blue-600 rounded-full transition-all duration-300"
           :style="{ width: uploadProgress + '%' }"></div>
    </div>
    <p class="text-xs text-gray-500 mt-1" x-text="uploadProgress + '% hochgeladen'"></p>
  </div>
</div>
```

---

## 4. live_preview.html (iframe Container)

The preview is loaded in an iframe that refreshes via HTMX when content changes.

```html
{# templates/editor/partials/live_preview.html #}

{# This is the preview container -- the actual iframe is in editor_base.html #}
{# This partial is used as a standalone preview page if needed #}

<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <style>
    body {
      margin: 0;
      padding: 0;
      background: #f3f4f6;
      display: flex;
      justify-content: center;
    }
    .preview-page {
      background: white;
      width: 210mm;
      min-height: 297mm;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
  </style>
</head>
<body>
  <div class="preview-page">
    {{ rendered_html|safe }}
  </div>
</body>
</html>
```

**Note on `{{ rendered_html|safe }}`:** The `rendered_html` variable is generated server-side by the `PDFRenderingService.render_to_html()` method from trusted Django templates and user content stored in the database. User text content within those templates is auto-escaped by the Django template engine. The `|safe` filter is applied only to the final rendered output from our own template engine, not to raw user input. If any user-supplied HTML is ever accepted (e.g., rich text descriptions), it must be sanitized server-side using a library such as `bleach` before storage.

---

## 5. template_selector.html (Grid with Previews)

```html
{# templates/editor/partials/template_selector.html #}

<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
     x-data="{ selectedCategory: 'all' }"
     @keyup.escape="this.remove()">

  <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[85vh] flex flex-col"
       @click.stop>

    {# Header #}
    <div class="p-6 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
      <div>
        <h2 class="text-xl font-semibold">Vorlage waehlen</h2>
        <p class="text-sm text-gray-500 mt-1">Ihr Inhalt bleibt erhalten -- nur das Design aendert sich.</p>
      </div>
      <button type="button"
              onclick="document.getElementById('modal-container').textContent = ''"
              class="text-gray-400 hover:text-gray-600 transition">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    {# Category filter #}
    <div class="px-6 py-3 border-b border-gray-100 flex gap-2 overflow-x-auto flex-shrink-0">
      <button @click="selectedCategory = 'all'"
              :class="selectedCategory === 'all' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'"
              class="px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition">
        Alle
      </button>
      {% for value, label in categories %}
        <button @click="selectedCategory = '{{ value }}'"
                :class="selectedCategory === '{{ value }}' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'"
                class="px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap transition">
          {{ label }}
        </button>
      {% endfor %}
    </div>

    {# Template grid #}
    <div class="flex-1 overflow-y-auto p-6">
      <div class="grid grid-cols-3 gap-4">
        {% for template in templates %}
          <div class="template-card relative group cursor-pointer"
               x-show="selectedCategory === 'all' || selectedCategory === '{{ template.category }}'"
               hx-post="{% url 'editor:template_select' document_id=document.id %}"
               hx-vals='{"template_slug": "{{ template.slug }}"}'
               hx-target="#modal-container"
               hx-swap="innerHTML">

            {# Thumbnail #}
            <div class="aspect-[210/297] bg-gray-100 rounded-lg overflow-hidden border-2 transition
                        {% if template.id == current_template.id %}border-blue-500{% else %}border-transparent group-hover:border-blue-300{% endif %}">
              {% if template.thumbnail %}
                <img src="{{ template.thumbnail.url }}"
                     alt="{{ template.name }}"
                     class="w-full h-full object-cover"
                     loading="lazy">
              {% else %}
                <div class="w-full h-full flex items-center justify-center text-gray-400 text-sm">
                  Vorschau
                </div>
              {% endif %}
            </div>

            {# Template name + badge #}
            <div class="mt-2 flex items-center justify-between">
              <span class="text-sm font-medium">{{ template.name }}</span>
              {% if template.is_premium and not is_premium %}
                <span class="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full">Premium</span>
              {% endif %}
            </div>

            {# Current indicator #}
            {% if template.id == current_template.id %}
              <div class="absolute top-2 right-2 bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
                Aktuell
              </div>
            {% endif %}

            {# Hover overlay for preview #}
            <div class="absolute inset-0 bg-blue-600/0 group-hover:bg-blue-600/10 rounded-lg transition flex items-center justify-center">
              <span class="opacity-0 group-hover:opacity-100 transition bg-white px-3 py-1 rounded-full text-sm font-medium shadow">
                Auswaehlen
              </span>
            </div>
          </div>
        {% endfor %}
      </div>
    </div>

  </div>
</div>
```

---

## 6. Alpine.js Patterns

```javascript
// templates/editor/js/editor_app.js

function editorApp() {
  return {
    activeSection: '{{ active_section.id|default:"" }}',
    previewScale: 0.5,
    isDirty: false,

    // Initialize Sortable.js for section reordering
    initSortable(el) {
      if (typeof Sortable === 'undefined') return;

      new Sortable(el, {
        animation: 150,
        handle: '.drag-handle',
        ghostClass: 'bg-blue-100',
        onEnd: function(evt) {
          var items = el.querySelectorAll('.section-item');
          var sectionIds = Array.from(items).map(
            function(item) { return item.dataset.sectionId; }
          );

          // Send new order to server
          fetch('{% url "editor:section_reorder" document_id=document.id %}', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ section_ids: sectionIds }),
          }).then(function() {
            // Trigger preview refresh
            htmx.trigger(document.body, 'preview-refresh');
          });
        },
      });
    },

    // Toggle section visibility
    toggleVisibility(sectionId) {
      // HTMX call to toggle is_visible
      htmx.ajax('POST', '/api/editor/sections/' + sectionId + '/toggle-visibility/', {
        target: '[data-section-id="' + sectionId + '"]',
        swap: 'outerHTML',
      });
    },

    // Auto-save status indicator
    showSaveStatus() {
      var indicator = document.getElementById('save-indicator');
      var status = document.getElementById('save-status');
      if (indicator) indicator.classList.add('hidden');
      if (status) {
        status.classList.remove('hidden');
        setTimeout(function() { status.classList.add('hidden'); }, 2000);
      }
    },
  };
}


// Photo uploader Alpine component
function photoUploader() {
  return {
    isDragging: false,
    showCropModal: false,
    cropImageSrc: '',
    cropper: null,
    uploading: false,
    uploadProgress: 0,
    selectedFile: null,

    handleDrop(event) {
      this.isDragging = false;
      var files = event.dataTransfer.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    },

    handleFileSelect(event) {
      var files = event.target.files;
      if (files.length > 0) {
        this.processFile(files[0]);
      }
    },

    processFile(file) {
      // Validate
      if (file.size > 5 * 1024 * 1024) {
        alert('Die Datei ist zu gross (max. 5 MB).');
        return;
      }
      if (['image/jpeg', 'image/png', 'image/webp'].indexOf(file.type) === -1) {
        alert('Nur JPEG, PNG und WebP sind erlaubt.');
        return;
      }

      this.selectedFile = file;
      this.cropImageSrc = URL.createObjectURL(file);
      this.showCropModal = true;

      // Initialize Cropper.js after image loads
      var self = this;
      this.$nextTick(function() {
        var img = self.$refs.cropImage;
        if (self.cropper) self.cropper.destroy();
        self.cropper = new Cropper(img, {
          aspectRatio: 3.5 / 4.5, // Standard passport photo ratio
          viewMode: 1,
          autoCropArea: 0.8,
          responsive: true,
        });
      });
    },

    cancelCrop() {
      this.showCropModal = false;
      if (this.cropper) {
        this.cropper.destroy();
        this.cropper = null;
      }
      if (this.cropImageSrc) {
        URL.revokeObjectURL(this.cropImageSrc);
      }
    },

    applyCrop() {
      if (!this.cropper) return;

      var cropData = this.cropper.getData(true); // rounded values

      // Create FormData with file + crop coordinates
      var formData = new FormData();
      formData.append('photo', this.selectedFile);
      formData.append('crop_x', cropData.x);
      formData.append('crop_y', cropData.y);
      formData.append('crop_width', cropData.width);
      formData.append('crop_height', cropData.height);

      this.showCropModal = false;
      this.uploading = true;
      this.uploadProgress = 0;

      // Upload via XMLHttpRequest with progress
      var self = this;
      var xhr = new XMLHttpRequest();
      xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
          self.uploadProgress = Math.round((e.loaded / e.total) * 100);
        }
      });
      xhr.addEventListener('load', function() {
        self.uploading = false;
        if (xhr.status === 200) {
          var container = document.getElementById('photo-preview-container');
          if (container) container.textContent = '';
          // Use DOM methods to safely insert response
          var template = document.createElement('template');
          template.innerHTML = xhr.responseText.trim();
          container.appendChild(template.content);
          htmx.trigger(document.body, 'preview-refresh');
        }
      });
      xhr.addEventListener('error', function() {
        self.uploading = false;
        alert('Fehler beim Hochladen. Bitte versuchen Sie es erneut.');
      });

      var documentId = '{{ document.id }}';
      xhr.open('POST', '/api/editor/' + documentId + '/photo/');
      var csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfEl) xhr.setRequestHeader('X-CSRFToken', csrfEl.value);
      xhr.send(formData);

      // Cleanup
      this.cropper.destroy();
      this.cropper = null;
      URL.revokeObjectURL(this.cropImageSrc);
    },

    removePhoto() {
      htmx.trigger(document.body, 'preview-refresh');
    },
  };
}


// Listen for HTMX after-settle events for save status
document.body.addEventListener('htmx:afterSettle', function(event) {
  // Show "Gespeichert" indicator after autosave
  if (event.detail.requestConfig && event.detail.requestConfig.verb === 'put') {
    var status = document.getElementById('save-status');
    if (status) {
      status.classList.remove('hidden');
      setTimeout(function() { status.classList.add('hidden'); }, 2000);
    }
  }
});
```

---

## 7. CSS Structure (editor.css)

```css
/* static/css/editor.css */

/* ── Editor Layout ─────────────────────────────── */
.editor-layout {
  display: flex;
  height: calc(100vh - 56px); /* toolbar height */
  overflow: hidden;
}

/* ── Section Sidebar ───────────────────────────── */
#section-sidebar {
  width: 14rem;
  flex-shrink: 0;
  border-right: 1px solid #e5e7eb;
  background: white;
  display: flex;
  flex-direction: column;
}

#section-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.section-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 150ms;
  user-select: none;
}

.section-item:hover {
  background-color: #f9fafb;
}

.section-item.active {
  background-color: #eff6ff;
  color: #1d4ed8;
}

/* Sortable.js ghost */
.section-item.sortable-ghost {
  opacity: 0.4;
  background-color: #dbeafe;
}

/* ── Form Area ─────────────────────────────────── */
#section-form-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #f9fafb;
}

/* Form inputs */
#section-form-area input[type="text"],
#section-form-area input[type="email"],
#section-form-area input[type="tel"],
#section-form-area input[type="url"],
#section-form-area input[type="date"],
#section-form-area input[type="month"],
#section-form-area textarea,
#section-form-area select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 150ms, box-shadow 150ms;
}

#section-form-area input:focus,
#section-form-area textarea:focus,
#section-form-area select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Entry card */
.entry-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: box-shadow 150ms;
}

.entry-card:hover {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* ── Preview Pane ──────────────────────────────── */
.preview-pane {
  width: 420px;
  flex-shrink: 0;
  background: #e5e7eb;
  border-left: 1px solid #d1d5db;
  display: flex;
  flex-direction: column;
}

.preview-pane iframe {
  background: white;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  border: 1px solid #d1d5db;
}

/* ── HTMX Indicators ──────────────────────────── */
.htmx-indicator {
  display: none;
}

.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator {
  display: inline;
}

/* ── Responsive: hide preview on small screens ── */
@media (max-width: 1024px) {
  .preview-pane {
    display: none;
  }

  #section-sidebar {
    width: 12rem;
  }
}

@media (max-width: 768px) {
  #section-sidebar {
    display: none;
  }
}
```
