// --- Auth ---

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_staff?: boolean
  profile: UserProfile | null
}

export type Anrede = 'herr' | 'frau' | 'divers' | 'keine'

export type Bundesland =
  | '' | 'BW' | 'BY' | 'BE' | 'BB' | 'HB' | 'HH'
  | 'HE' | 'MV' | 'NI' | 'NW' | 'RP' | 'SL'
  | 'SN' | 'ST' | 'SH' | 'TH'

export type SubscriptionPlan = 'free' | 'premium_monthly' | 'premium_yearly' | 'business'

export interface UserProfile {
  anrede: Anrede
  geburtsdatum: string | null
  telefon: string
  strasse: string
  plz: string
  stadt: string
  bundesland: Bundesland
  subscription_plan: SubscriptionPlan
  subscription_expires_at: string | null
  preferred_language: 'de' | 'en'
  privacy_accepted_at: string | null
  marketing_consent: boolean
  newsletter_consent: boolean
}

export interface AuthTokens {
  access: string
  refresh: string
}

// --- Documents ---

export type DocType = 'lebenslauf' | 'anschreiben' | 'deckblatt'

export type SectionType =
  | 'persoenliche_daten'
  | 'berufserfahrung'
  | 'ausbildung'
  | 'kenntnisse'
  | 'sprachen'
  | 'weiterbildungen'
  | 'ehrenamt'
  | 'interessen'
  | 'unterschrift'

export interface Document {
  id: string
  doc_type: DocType
  title: string
  content: Record<string, unknown>
  template: string | null
  theme: string
  is_premium: boolean
  pdf_file: string | null
  sections: Section[]
  created_at: string
  updated_at: string
}

export interface Section {
  id: string
  section_type: SectionType
  title: string
  content: Record<string, unknown>
  ordering: number
  is_visible: boolean
}

// --- Section Content Schemas (matching documents/schemas.py) ---

export interface PersoenlicheDaten {
  foto: string
  anrede: string
  vorname: string
  nachname: string
  geburtsdatum: string
  geburtsort: string
  staatsangehoerigkeit: string
  familienstand: string
  email: string
  telefon: string
  strasse: string
  plz: string
  stadt: string
  website: string
  linkedin: string
  xing: string
}

export interface BerufserfahrungEntry {
  id: string
  position: string
  unternehmen: string
  ort: string
  von: string
  bis: string
  ist_aktuell: boolean
  beschreibung: string
  aufgaben: string[]
}

export interface BerufserfahrungContent {
  eintraege: BerufserfahrungEntry[]
}

export interface AusbildungEntry {
  id: string
  abschluss: string
  fachrichtung: string
  institution: string
  ort: string
  von: string
  bis: string
  note: string
  beschreibung: string
}

export interface AusbildungContent {
  eintraege: AusbildungEntry[]
}

export interface KenntnisEntry {
  id: string
  name: string
  kategorie: string
  niveau: number // 1-5
}

export interface KenntnisseContent {
  eintraege: KenntnisEntry[]
}

export interface SpracheEntry {
  id: string
  sprache: string
  niveau: string // A1, A2, B1, B2, C1, C2
  ist_muttersprache: boolean
}

export interface SprachenContent {
  eintraege: SpracheEntry[]
}

export interface WeiterbildungEntry {
  id: string
  titel: string
  anbieter: string
  datum: string
  beschreibung: string
}

export interface WeiterbildungenContent {
  eintraege: WeiterbildungEntry[]
}

export interface EhrenamtEntry {
  id: string
  rolle: string
  organisation: string
  von: string
  bis: string
  beschreibung: string
}

export interface EhrenamtContent {
  eintraege: EhrenamtEntry[]
}

export interface InteressenContent {
  interessen: string[]
}

export interface UnterschriftContent {
  ort: string
  datum: string
  unterschrift_bild: string
}

// --- Templates ---

export type TemplateCategory = 'klassisch' | 'modern' | 'kreativ' | 'akademisch' | 'it_tech' | 'student'

export interface Template {
  id: string
  name: string
  slug: string
  category: TemplateCategory
  description: string
  thumbnail: string
  html_template: string
  css_styles: string
  is_premium: boolean
  is_active: boolean
  ordering: number
}

// --- Jobs ---

export interface Job {
  id: string
  title: string
  company: string
  location: string
  url: string
  source: string
  description: string
  salary_range: string
  scraped_at: string
  is_saved: boolean
}

// --- Pipeline ---

export type ApplicationStatus =
  | 'discovered'
  | 'saved'
  | 'applied'
  | 'waiting'
  | 'interview'
  | 'follow_up'
  | 'offer'
  | 'rejected'

export interface Application {
  id: string
  job: Job
  document: Document | null
  cover_letter: CoverLetter | null
  status: ApplicationStatus
  applied_at: string | null
  notes: string
  next_action: string | null
  next_action_date: string | null
}

// --- Cover Letters ---

export interface CoverLetter {
  id: string
  job: string
  document: string
  content: string
  tone: 'formal' | 'modern' | 'kreativ'
  language: string
  generated_at: string
}

// --- Payments ---

export interface SubscriptionInfo {
  plan: SubscriptionPlan
  expires_at: string | null
  is_active: boolean
}

export interface Invoice {
  id: string
  rechnungsnummer: string
  datum: string
  betrag: string
  pdf_url: string | null
}

// --- API ---

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  detail?: string
  [key: string]: unknown
}
