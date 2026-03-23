<script setup lang="ts">
import { computed } from 'vue'
import { useEditorStore } from '@/stores/editor'
import type {
  Section,
  PersoenlicheDaten,
  BerufserfahrungContent,
  AusbildungContent,
  KenntnisseContent,
  SprachenContent,
  WeiterbildungenContent,
  EhrenamtContent,
  InteressenContent,
  UnterschriftContent,
} from '@/types'

const editor = useEditorStore()

const visibleSections = computed(() =>
  editor.orderedSections.filter((s) => s.is_visible)
)

// --- Typed content accessors ---

function persoenlich(s: Section): PersoenlicheDaten {
  return s.content as unknown as PersoenlicheDaten
}

function beruf(s: Section): BerufserfahrungContent {
  return s.content as unknown as BerufserfahrungContent
}

function ausbildung(s: Section): AusbildungContent {
  return s.content as unknown as AusbildungContent
}

function kenntnisse(s: Section): KenntnisseContent {
  return s.content as unknown as KenntnisseContent
}

function sprachen(s: Section): SprachenContent {
  return s.content as unknown as SprachenContent
}

function weiterbildungen(s: Section): WeiterbildungenContent {
  return s.content as unknown as WeiterbildungenContent
}

function ehrenamt(s: Section): EhrenamtContent {
  return s.content as unknown as EhrenamtContent
}

function interessen(s: Section): InteressenContent {
  return s.content as unknown as InteressenContent
}

function unterschrift(s: Section): UnterschriftContent {
  return s.content as unknown as UnterschriftContent
}

function fullName(d: PersoenlicheDaten): string {
  return [d.vorname, d.nachname].filter(Boolean).join(' ')
}

function formatDateRange(von: string, bis: string, istAktuell?: boolean): string {
  const parts: string[] = []
  if (von) parts.push(von)
  if (istAktuell) {
    parts.push('heute')
  } else if (bis) {
    parts.push(bis)
  }
  return parts.join(' – ')
}

function niveauPercent(n: number): number {
  return Math.max(0, Math.min(100, (n / 5) * 100))
}
</script>

<template>
  <div class="cv-preview">
    <template v-for="section in visibleSections" :key="section.id">
      <!-- Persoenliche Daten -->
      <div v-if="section.section_type === 'persoenliche_daten'" class="cv-header">
        <h1 class="cv-name">{{ fullName(persoenlich(section)) }}</h1>
        <div class="cv-contact">
          <span v-if="persoenlich(section).email">{{ persoenlich(section).email }}</span>
          <span v-if="persoenlich(section).telefon">{{ persoenlich(section).telefon }}</span>
          <span v-if="persoenlich(section).stadt">{{ persoenlich(section).stadt }}</span>
        </div>
        <div class="cv-details">
          <span v-if="persoenlich(section).geburtsdatum">
            Geb. {{ persoenlich(section).geburtsdatum }}<template v-if="persoenlich(section).geburtsort">, {{ persoenlich(section).geburtsort }}</template>
          </span>
          <span v-if="persoenlich(section).staatsangehoerigkeit">{{ persoenlich(section).staatsangehoerigkeit }}</span>
          <span v-if="persoenlich(section).familienstand">{{ persoenlich(section).familienstand }}</span>
        </div>
        <div class="cv-links">
          <span v-if="persoenlich(section).linkedin">LinkedIn: {{ persoenlich(section).linkedin }}</span>
          <span v-if="persoenlich(section).xing">Xing: {{ persoenlich(section).xing }}</span>
          <span v-if="persoenlich(section).website">{{ persoenlich(section).website }}</span>
        </div>
      </div>

      <!-- Berufserfahrung -->
      <div v-else-if="section.section_type === 'berufserfahrung'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Berufserfahrung' }}</h2>
        <div class="cv-divider" />
        <div
          v-for="entry in beruf(section).eintraege ?? []"
          :key="entry.id"
          class="cv-entry"
        >
          <div class="cv-entry-header">
            <strong>{{ entry.position }}</strong>
            <span class="cv-date">{{ formatDateRange(entry.von, entry.bis, entry.ist_aktuell) }}</span>
          </div>
          <div class="cv-entry-sub">
            {{ entry.unternehmen }}<template v-if="entry.ort">, {{ entry.ort }}</template>
          </div>
          <p v-if="entry.beschreibung" class="cv-entry-desc">{{ entry.beschreibung }}</p>
          <ul v-if="entry.aufgaben?.length" class="cv-tasks">
            <li v-for="(aufgabe, i) in entry.aufgaben" :key="i">{{ aufgabe }}</li>
          </ul>
        </div>
      </div>

      <!-- Ausbildung -->
      <div v-else-if="section.section_type === 'ausbildung'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Ausbildung' }}</h2>
        <div class="cv-divider" />
        <div
          v-for="entry in ausbildung(section).eintraege ?? []"
          :key="entry.id"
          class="cv-entry"
        >
          <div class="cv-entry-header">
            <strong>{{ entry.abschluss }}<template v-if="entry.fachrichtung"> — {{ entry.fachrichtung }}</template></strong>
            <span class="cv-date">{{ formatDateRange(entry.von, entry.bis) }}</span>
          </div>
          <div class="cv-entry-sub">
            {{ entry.institution }}<template v-if="entry.ort">, {{ entry.ort }}</template>
          </div>
          <p v-if="entry.note" class="cv-entry-desc">Note: {{ entry.note }}</p>
          <p v-if="entry.beschreibung" class="cv-entry-desc">{{ entry.beschreibung }}</p>
        </div>
      </div>

      <!-- Kenntnisse -->
      <div v-else-if="section.section_type === 'kenntnisse'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Kenntnisse' }}</h2>
        <div class="cv-divider" />
        <div class="cv-skills-grid">
          <div
            v-for="entry in kenntnisse(section).eintraege ?? []"
            :key="entry.id"
            class="cv-skill"
          >
            <div class="cv-skill-header">
              <span>{{ entry.name }}</span>
              <span v-if="entry.kategorie" class="cv-skill-cat">{{ entry.kategorie }}</span>
            </div>
            <div class="cv-skill-bar">
              <div class="cv-skill-fill" :style="{ width: niveauPercent(entry.niveau) + '%' }" />
            </div>
          </div>
        </div>
      </div>

      <!-- Sprachen -->
      <div v-else-if="section.section_type === 'sprachen'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Sprachen' }}</h2>
        <div class="cv-divider" />
        <div class="cv-lang-list">
          <div
            v-for="entry in sprachen(section).eintraege ?? []"
            :key="entry.id"
            class="cv-lang"
          >
            <span class="cv-lang-name">{{ entry.sprache }}</span>
            <span class="cv-lang-badge">
              {{ entry.ist_muttersprache ? 'Muttersprache' : entry.niveau }}
            </span>
          </div>
        </div>
      </div>

      <!-- Weiterbildungen -->
      <div v-else-if="section.section_type === 'weiterbildungen'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Weiterbildungen' }}</h2>
        <div class="cv-divider" />
        <div
          v-for="entry in weiterbildungen(section).eintraege ?? []"
          :key="entry.id"
          class="cv-entry"
        >
          <div class="cv-entry-header">
            <strong>{{ entry.titel }}</strong>
            <span v-if="entry.datum" class="cv-date">{{ entry.datum }}</span>
          </div>
          <div v-if="entry.anbieter" class="cv-entry-sub">{{ entry.anbieter }}</div>
          <p v-if="entry.beschreibung" class="cv-entry-desc">{{ entry.beschreibung }}</p>
        </div>
      </div>

      <!-- Ehrenamt -->
      <div v-else-if="section.section_type === 'ehrenamt'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Ehrenamt' }}</h2>
        <div class="cv-divider" />
        <div
          v-for="entry in ehrenamt(section).eintraege ?? []"
          :key="entry.id"
          class="cv-entry"
        >
          <div class="cv-entry-header">
            <strong>{{ entry.rolle }}</strong>
            <span class="cv-date">{{ formatDateRange(entry.von, entry.bis) }}</span>
          </div>
          <div class="cv-entry-sub">{{ entry.organisation }}</div>
          <p v-if="entry.beschreibung" class="cv-entry-desc">{{ entry.beschreibung }}</p>
        </div>
      </div>

      <!-- Interessen -->
      <div v-else-if="section.section_type === 'interessen'" class="cv-section">
        <h2 class="cv-section-title">{{ section.title || 'Interessen' }}</h2>
        <div class="cv-divider" />
        <p class="cv-interests">
          {{ (interessen(section).interessen ?? []).join(', ') }}
        </p>
      </div>

      <!-- Unterschrift -->
      <div v-else-if="section.section_type === 'unterschrift'" class="cv-section cv-signature">
        <div class="cv-sig-line">
          {{ [unterschrift(section).ort, unterschrift(section).datum].filter(Boolean).join(', ') }}
        </div>
        <div class="cv-sig-placeholder" />
      </div>
    </template>

    <!-- Empty state -->
    <div v-if="visibleSections.length === 0" class="cv-empty">
      <p>Keine sichtbaren Abschnitte vorhanden.</p>
    </div>
  </div>
</template>

<style scoped>
.cv-preview {
  padding: 48px 56px;
  font-family: 'Times New Roman', 'Georgia', 'Noto Serif', serif;
  font-size: 11px;
  line-height: 1.5;
  color: #1a1a1a;
  background: #fff;
  min-height: 100%;
}

/* --- Header (persoenliche_daten) --- */
.cv-header {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #4338ca;
}

.cv-name {
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin: 0 0 8px;
  color: #111;
}

.cv-contact {
  display: flex;
  justify-content: center;
  gap: 16px;
  font-size: 10.5px;
  color: #444;
  flex-wrap: wrap;
}

.cv-details,
.cv-links {
  display: flex;
  justify-content: center;
  gap: 16px;
  font-size: 9.5px;
  color: #666;
  margin-top: 4px;
  flex-wrap: wrap;
}

/* --- Section --- */
.cv-section {
  margin-bottom: 18px;
}

.cv-section-title {
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #4338ca;
  margin: 0 0 4px;
}

.cv-divider {
  height: 1px;
  background: #d1d5db;
  margin-bottom: 10px;
}

/* --- Entries (beruf, ausbildung, weiterbildung, ehrenamt) --- */
.cv-entry {
  margin-bottom: 10px;
}

.cv-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
}

.cv-entry-header strong {
  font-size: 11px;
}

.cv-date {
  font-size: 9.5px;
  color: #666;
  white-space: nowrap;
}

.cv-entry-sub {
  font-size: 10px;
  color: #555;
  margin-top: 1px;
}

.cv-entry-desc {
  margin: 4px 0 0;
  font-size: 10.5px;
  color: #333;
}

.cv-tasks {
  margin: 4px 0 0 16px;
  padding: 0;
  font-size: 10.5px;
  color: #333;
}

.cv-tasks li {
  margin-bottom: 2px;
}

/* --- Kenntnisse (skills with bars) --- */
.cv-skills-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 20px;
}

.cv-skill-header {
  display: flex;
  justify-content: space-between;
  font-size: 10.5px;
  margin-bottom: 2px;
}

.cv-skill-cat {
  font-size: 9px;
  color: #888;
}

.cv-skill-bar {
  height: 5px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.cv-skill-fill {
  height: 100%;
  background: #4338ca;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* --- Sprachen --- */
.cv-lang-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
}

.cv-lang {
  display: flex;
  align-items: center;
  gap: 6px;
}

.cv-lang-name {
  font-size: 10.5px;
}

.cv-lang-badge {
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  font-size: 9px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 3px;
  background: #eef2ff;
  color: #4338ca;
}

/* --- Interessen --- */
.cv-interests {
  font-size: 10.5px;
  color: #333;
  margin: 0;
}

/* --- Unterschrift --- */
.cv-signature {
  margin-top: 32px;
}

.cv-sig-line {
  font-size: 10.5px;
  color: #333;
  margin-bottom: 28px;
}

.cv-sig-placeholder {
  width: 180px;
  border-bottom: 1px solid #999;
}

/* --- Empty state --- */
.cv-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #999;
  font-size: 12px;
}
</style>
