import type { Anrede, Bundesland, DocType, SectionType, TemplateCategory } from '@/types'

export const ANREDE_OPTIONS: { value: Anrede; label: string }[] = [
  { value: 'herr', label: 'Herr' },
  { value: 'frau', label: 'Frau' },
  { value: 'divers', label: 'Divers' },
  { value: 'keine', label: 'Keine Angabe' },
]

export const BUNDESLAENDER: { value: Bundesland; label: string }[] = [
  { value: '', label: 'Bitte wahlen' },
  { value: 'BW', label: 'Baden-Wurttemberg' },
  { value: 'BY', label: 'Bayern' },
  { value: 'BE', label: 'Berlin' },
  { value: 'BB', label: 'Brandenburg' },
  { value: 'HB', label: 'Bremen' },
  { value: 'HH', label: 'Hamburg' },
  { value: 'HE', label: 'Hessen' },
  { value: 'MV', label: 'Mecklenburg-Vorpommern' },
  { value: 'NI', label: 'Niedersachsen' },
  { value: 'NW', label: 'Nordrhein-Westfalen' },
  { value: 'RP', label: 'Rheinland-Pfalz' },
  { value: 'SL', label: 'Saarland' },
  { value: 'SN', label: 'Sachsen' },
  { value: 'ST', label: 'Sachsen-Anhalt' },
  { value: 'SH', label: 'Schleswig-Holstein' },
  { value: 'TH', label: 'Thuringen' },
]

export const DOC_TYPES: { value: DocType; label: string }[] = [
  { value: 'lebenslauf', label: 'Lebenslauf' },
  { value: 'anschreiben', label: 'Anschreiben' },
  { value: 'deckblatt', label: 'Deckblatt' },
]

export const SECTION_TYPES: { value: SectionType; label: string; icon: string }[] = [
  { value: 'persoenliche_daten', label: 'Personliche Daten', icon: 'User' },
  { value: 'berufserfahrung', label: 'Berufserfahrung', icon: 'Briefcase' },
  { value: 'ausbildung', label: 'Ausbildung', icon: 'GraduationCap' },
  { value: 'kenntnisse', label: 'Kenntnisse', icon: 'Wrench' },
  { value: 'sprachen', label: 'Sprachen', icon: 'Globe' },
  { value: 'weiterbildungen', label: 'Weiterbildungen', icon: 'Award' },
  { value: 'ehrenamt', label: 'Ehrenamt', icon: 'Heart' },
  { value: 'interessen', label: 'Interessen', icon: 'Star' },
  { value: 'unterschrift', label: 'Unterschrift', icon: 'PenTool' },
]

export const TEMPLATE_CATEGORIES: { value: TemplateCategory | 'alle'; label: string }[] = [
  { value: 'alle', label: 'Alle' },
  { value: 'klassisch', label: 'Klassisch' },
  { value: 'modern', label: 'Modern' },
  { value: 'kreativ', label: 'Kreativ' },
  { value: 'akademisch', label: 'Akademisch' },
  { value: 'it_tech', label: 'IT & Tech' },
  { value: 'student', label: 'Student' },
]

export const SPRACH_NIVEAUS = [
  { value: 'A1', label: 'A1 - Anfanger' },
  { value: 'A2', label: 'A2 - Grundlegende Kenntnisse' },
  { value: 'B1', label: 'B1 - Fortgeschrittene Sprachverwendung' },
  { value: 'B2', label: 'B2 - Selbstandige Sprachverwendung' },
  { value: 'C1', label: 'C1 - Fachkundige Sprachkenntnisse' },
  { value: 'C2', label: 'C2 - Annahernd muttersprachlich' },
]

export const SUBSCRIPTION_PLANS = [
  {
    id: 'free',
    name: 'Kostenlos',
    price: '0',
    period: '',
    features: ['1 Dokument', '3 Schriftarten', '30 Designs'],
    highlighted: false,
  },
  {
    id: 'premium_monthly',
    name: 'Premium Monatlich',
    price: '17,99',
    period: '/Monat',
    features: ['Unbegrenzte Dokumente', 'Alle Schriftarten', 'Alle Designs', 'PDF-Export', 'KI-Optimierung'],
    highlighted: true,
  },
  {
    id: 'premium_yearly',
    name: 'Premium Jahrlich',
    price: '109,99',
    period: '/Jahr',
    features: ['Alles aus Premium', 'Sparen Sie 40%', 'Prioritatssupport'],
    highlighted: false,
  },
  {
    id: 'business',
    name: 'Business',
    price: '34,99',
    period: '/Quartal',
    features: ['Alles aus Premium', 'Team-Verwaltung', 'API-Zugang'],
    highlighted: false,
  },
]
