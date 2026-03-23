<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  ArrowRight, CheckCircle2, ChevronDown, Menu, X,
  Star, Download, Lock, Clock, Sparkles,
  LayoutTemplate, MousePointerClick, Terminal, Zap,
  Shield, Code2, Command,
} from 'lucide-vue-next'
import Button from '@/components/ui/Button.vue'
import { SUBSCRIPTION_PLANS } from '@/lib/constants'
import PricingCard from '@/components/billing/PricingCard.vue'

const mobileMenuOpen = ref(false)

// FAQ
const faqs = [
  {
    q: 'Ist GetResume wirklich kostenlos?',
    a: 'Ja — erstellen Sie kostenlos einen Lebenslauf und laden Sie ihn als PDF herunter. Premium-Vorlagen und KI-Optimierung sind im kostenpflichtigen Abo enthalten.',
  },
  {
    q: 'Sind meine Daten sicher?',
    a: 'Ihre Daten werden DSGVO-konform in deutschen Rechenzentren gespeichert. SSL-Verschlusselung, keine externen Tracker, keine Google Fonts.',
  },
  {
    q: 'Was bedeutet ATS-optimiert?',
    a: 'ATS (Applicant Tracking System) ist die Software, die Unternehmen zum Filtern von Bewerbungen verwenden. Unsere Vorlagen sind so gestaltet, dass sie korrekt geparst werden.',
  },
  {
    q: 'Kann ich meinen Lebenslauf jederzeit bearbeiten?',
    a: 'Ja — alle Dokumente werden automatisch gespeichert. Sie konnen jederzeit zuruckkehren und Anderungen vornehmen.',
  },
  {
    q: 'Welche Zahlungsmethoden akzeptieren Sie?',
    a: 'Kreditkarten (Visa, Mastercard), SEPA-Lastschrift und PayPal. Alle Preise inkl. 19% MwSt.',
  },
]
const openFaq = ref<number | null>(null)
function toggleFaq(i: number) {
  openFaq.value = openFaq.value === i ? null : i
}

const features = [
  {
    icon: LayoutTemplate,
    title: '30+ Vorlagen',
    description: 'Branchenspezifische Designs, erstellt von HR-Experten. ATS-optimiert und sofort einsatzbereit.',
    accent: 'text-indigo-400',
    glow: 'bg-indigo-500/10',
    border: 'border-indigo-500/10',
  },
  {
    icon: MousePointerClick,
    title: 'Drag & Drop Editor',
    description: 'Abschnitte per Drag & Drop anordnen. Live-Vorschau und automatisches Speichern.',
    accent: 'text-cyan-400',
    glow: 'bg-cyan-500/10',
    border: 'border-cyan-500/10',
  },
  {
    icon: Sparkles,
    title: 'KI-Optimierung',
    description: 'Formulierungen automatisch verbessern. Wirkungsvolle Beschreibungen in Sekunden.',
    accent: 'text-violet-400',
    glow: 'bg-violet-500/10',
    border: 'border-violet-500/10',
  },
  {
    icon: Download,
    title: 'PDF-Export',
    description: 'Hochauflostes PDF in Druckqualitat. Pixel-perfekte Formatierung garantiert.',
    accent: 'text-emerald-400',
    glow: 'bg-emerald-500/10',
    border: 'border-emerald-500/10',
  },
  {
    icon: Lock,
    title: 'DSGVO-konform',
    description: 'Hosting in Deutschland. Keine Google Fonts, keine externen Tracker. SSL-verschlusselt.',
    accent: 'text-amber-400',
    glow: 'bg-amber-500/10',
    border: 'border-amber-500/10',
  },
  {
    icon: Zap,
    title: 'In 5 Minuten fertig',
    description: 'Vorlage wahlen, Daten eingeben, PDF herunterladen. So einfach ist das.',
    accent: 'text-rose-400',
    glow: 'bg-rose-500/10',
    border: 'border-rose-500/10',
  },
]

const steps = [
  { num: '01', title: 'Vorlage wahlen', desc: 'Aus 30+ professionellen Designs die passende Vorlage fur Ihre Branche wahlen.' },
  { num: '02', title: 'Inhalt eingeben', desc: 'Daten im intuitiven Editor eingeben. KI-Vorschlage helfen bei den Formulierungen.' },
  { num: '03', title: 'PDF exportieren', desc: 'Pixel-perfektes PDF herunterladen. ATS-optimiert und druckfertig.' },
]

const testimonials = [
  {
    name: 'Marie S.',
    role: 'Marketing Managerin',
    text: 'In 15 Minuten einen professionellen Lebenslauf erstellt. Die Vorlagen sind modern und ATS-optimiert.',
    rating: 5,
  },
  {
    name: 'Thomas K.',
    role: 'Software-Entwickler',
    text: 'Endlich eine Plattform, die DSGVO-konform ist und keine Google Fonts nutzt. Die KI-Optimierung ist beeindruckend.',
    rating: 5,
  },
  {
    name: 'Anna L.',
    role: 'Absolventin',
    text: 'Als Berufseinsteigerin genau die Struktur bekommen, die Personaler erwarten. Sehr intuitive Bedienung.',
    rating: 5,
  },
]

const templateCategories = [
  { name: 'Klassisch', color: 'indigo', accent: 'bg-indigo-500', badge: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' },
  { name: 'Modern', color: 'cyan', accent: 'bg-cyan-500', badge: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' },
  { name: 'Kreativ', color: 'violet', accent: 'bg-violet-500', badge: 'bg-violet-500/10 text-violet-400 border-violet-500/20' },
  { name: 'Akademisch', color: 'amber', accent: 'bg-amber-500', badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
  { name: 'IT & Tech', color: 'emerald', accent: 'bg-emerald-500', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
]
</script>

<template>
  <div class="min-h-screen bg-background text-foreground overflow-hidden">

    <!-- ═══════════════════ NAVBAR ═══════════════════ -->
    <header class="fixed top-0 inset-x-0 z-50 glass border-b border-white/[0.06]">
      <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <!-- Logo: terminal-style -->
        <RouterLink to="/" class="flex items-center gap-2.5 shrink-0 group">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 border border-indigo-500/20 font-mono text-sm font-bold text-indigo-400 group-hover:bg-indigo-500/20 transition-colors">
            &gt;_
          </div>
          <span class="text-lg font-semibold text-foreground">
            Get<span class="text-indigo-400">Resume</span>
          </span>
        </RouterLink>

        <!-- Desktop nav -->
        <nav class="hidden lg:flex items-center gap-1">
          <RouterLink to="/app/templates" class="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-foreground transition-colors">
            Vorlagen
          </RouterLink>
          <a href="#features" class="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-foreground transition-colors">
            Features
          </a>
          <a href="#pricing" class="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-foreground transition-colors">
            Preise
          </a>
        </nav>

        <!-- Desktop CTA -->
        <div class="hidden lg:flex items-center gap-4">
          <RouterLink to="/login" class="text-sm font-medium text-zinc-400 hover:text-foreground transition-colors">
            Anmelden
          </RouterLink>
          <RouterLink to="/register">
            <Button class="glow-sm hover:glow-md transition-shadow">
              Kostenlos starten
              <ArrowRight class="h-3.5 w-3.5" />
            </Button>
          </RouterLink>
        </div>

        <!-- Mobile toggle -->
        <button
          class="lg:hidden flex items-center justify-center h-9 w-9 rounded-lg text-zinc-400 hover:text-foreground hover:bg-white/5 transition-colors"
          @click="mobileMenuOpen = !mobileMenuOpen"
          aria-label="Menu"
        >
          <X v-if="mobileMenuOpen" class="h-5 w-5" />
          <Menu v-else class="h-5 w-5" />
        </button>
      </div>

      <!-- Mobile dropdown -->
      <Transition name="dropdown">
        <div v-if="mobileMenuOpen" class="lg:hidden border-t border-white/[0.06] glass px-6 py-4 space-y-1">
          <RouterLink to="/app/templates" class="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-400 hover:text-foreground hover:bg-white/5" @click="mobileMenuOpen = false">Vorlagen</RouterLink>
          <a href="#features" class="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-400 hover:text-foreground hover:bg-white/5" @click="mobileMenuOpen = false">Features</a>
          <a href="#pricing" class="block rounded-lg px-4 py-2.5 text-sm font-medium text-zinc-400 hover:text-foreground hover:bg-white/5" @click="mobileMenuOpen = false">Preise</a>
          <div class="pt-3 border-t border-white/[0.06] flex flex-col gap-2">
            <RouterLink to="/login" @click="mobileMenuOpen = false">
              <Button variant="outline" class="w-full">Anmelden</Button>
            </RouterLink>
            <RouterLink to="/register" @click="mobileMenuOpen = false">
              <Button class="w-full">Kostenlos starten</Button>
            </RouterLink>
          </div>
        </div>
      </Transition>
    </header>

    <!-- ═══════════════════ HERO ═══════════════════ -->
    <section class="relative min-h-screen flex items-center pt-16">
      <!-- Background layers -->
      <div class="absolute inset-0 bg-dots"></div>
      <!-- Gradient orbs -->
      <div class="absolute top-1/4 left-[15%] h-[500px] w-[500px] rounded-full bg-indigo-500/[0.07] blur-[120px] animate-pulse-slow"></div>
      <div class="absolute bottom-1/4 right-[10%] h-[400px] w-[400px] rounded-full bg-violet-500/[0.06] blur-[120px] animate-pulse-slow" style="animation-delay: 2s"></div>
      <div class="absolute top-[60%] left-[50%] h-[300px] w-[300px] rounded-full bg-cyan-500/[0.05] blur-[120px] animate-pulse-slow" style="animation-delay: 4s"></div>

      <div class="relative mx-auto max-w-7xl px-6 py-20 lg:py-32 w-full">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          <!-- Left: Text -->
          <div class="animate-fade-in">
            <!-- Version badge -->
            <div class="inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/5 px-4 py-1.5 text-sm font-mono text-indigo-400 mb-8">
              <span class="flex h-2 w-2 rounded-full bg-emerald-500 animate-[pulse-slow_2s_ease-in-out_infinite]"></span>
              v2.0 — jetzt mit KI-Optimierung
            </div>

            <!-- Headline -->
            <h1 class="font-mono text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.1] tracking-tight">
              Lebenslauf
              <br />
              erstellen.
              <br />
              <span class="text-gradient">Ohne Kompromisse.</span>
            </h1>

            <!-- Subtitle -->
            <p class="mt-6 text-lg lg:text-xl text-zinc-400 leading-relaxed max-w-xl">
              ATS-optimierte Vorlagen, KI-Textoptimierung und PDF-Export
              in Druckqualitat.
              <span class="text-zinc-300">DSGVO-konform und kostenlos.</span>
            </p>

            <!-- CTA -->
            <div class="mt-10 flex flex-col sm:flex-row gap-4">
              <RouterLink to="/register">
                <Button size="lg" class="h-13 px-8 text-base glow-md hover:glow-lg transition-all duration-300 hover:scale-[1.02]">
                  Lebenslauf erstellen
                  <ArrowRight class="h-4 w-4" />
                </Button>
              </RouterLink>
              <RouterLink to="/app/templates">
                <Button variant="outline" size="lg" class="h-13 px-8 text-base border-white/10 hover:border-white/20 hover:bg-white/5">
                  <LayoutTemplate class="h-4 w-4" />
                  Vorlagen ansehen
                </Button>
              </RouterLink>
            </div>

            <!-- Trust line (terminal-style) -->
            <p class="mt-6 text-sm text-zinc-500 font-mono flex items-center gap-2">
              <Terminal class="h-3.5 w-3.5 text-zinc-600" />
              kostenlos · keine Kreditkarte · DSGVO-konform
            </p>
          </div>

          <!-- Right: Product mockup (code-editor style) -->
          <div class="animate-scale-in relative">
            <!-- Glow behind -->
            <div class="absolute -inset-8 bg-gradient-to-br from-indigo-500/10 via-violet-500/5 to-cyan-500/10 rounded-3xl blur-3xl"></div>

            <!-- Editor window -->
            <div class="relative rounded-2xl border border-white/[0.08] bg-[#0d0d11] overflow-hidden shadow-2xl shadow-black/50">
              <!-- Tab bar -->
              <div class="flex items-center gap-3 px-4 py-3 border-b border-white/[0.06] bg-[#0a0a0e]">
                <div class="flex gap-1.5">
                  <div class="h-3 w-3 rounded-full bg-zinc-700 hover:bg-red-500/80 transition-colors"></div>
                  <div class="h-3 w-3 rounded-full bg-zinc-700 hover:bg-amber-500/80 transition-colors"></div>
                  <div class="h-3 w-3 rounded-full bg-zinc-700 hover:bg-emerald-500/80 transition-colors"></div>
                </div>
                <div class="font-mono text-xs text-zinc-500 ml-2">lebenslauf.pdf — GetResume</div>
              </div>

              <!-- Resume content (dark themed) -->
              <div class="p-6 space-y-5">
                <!-- Name header -->
                <div class="border-b border-white/[0.06] pb-4">
                  <div class="flex items-center gap-4">
                    <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white font-mono font-bold text-lg">M</div>
                    <div>
                      <div class="font-mono text-lg text-foreground font-bold tracking-tight">Max Mustermann</div>
                      <div class="font-mono text-sm text-indigo-400">Senior Software Engineer</div>
                    </div>
                  </div>
                  <div class="flex flex-wrap gap-4 mt-3 text-xs text-zinc-500 font-mono">
                    <span>Berlin, DE</span>
                    <span>max@example.de</span>
                    <span>+49 171 000 0000</span>
                  </div>
                </div>

                <!-- Section: Berufserfahrung -->
                <div>
                  <div class="flex items-center gap-2 mb-3">
                    <div class="h-1 w-4 rounded-full bg-indigo-500"></div>
                    <span class="font-mono text-[11px] text-zinc-500 uppercase tracking-widest">Berufserfahrung</span>
                  </div>
                  <div class="ml-6 space-y-2">
                    <div class="flex items-center justify-between">
                      <div class="h-2 w-40 bg-zinc-800/80 rounded-full"></div>
                      <div class="text-[10px] font-mono text-zinc-600">2021 — heute</div>
                    </div>
                    <div class="h-1.5 w-full bg-zinc-800/50 rounded-full"></div>
                    <div class="h-1.5 w-4/5 bg-zinc-800/50 rounded-full"></div>
                    <div class="h-1.5 w-5/6 bg-zinc-800/50 rounded-full"></div>
                  </div>
                </div>

                <!-- Section: Kenntnisse -->
                <div>
                  <div class="flex items-center gap-2 mb-3">
                    <div class="h-1 w-4 rounded-full bg-cyan-500"></div>
                    <span class="font-mono text-[11px] text-zinc-500 uppercase tracking-widest">Kenntnisse</span>
                  </div>
                  <div class="ml-6 flex flex-wrap gap-2">
                    <span class="px-2.5 py-1 text-[11px] font-mono bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-md">TypeScript</span>
                    <span class="px-2.5 py-1 text-[11px] font-mono bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-md">React</span>
                    <span class="px-2.5 py-1 text-[11px] font-mono bg-violet-500/10 border border-violet-500/20 text-violet-400 rounded-md">Python</span>
                    <span class="px-2.5 py-1 text-[11px] font-mono bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-md">Docker</span>
                    <span class="px-2.5 py-1 text-[11px] font-mono bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-md">AWS</span>
                  </div>
                </div>

                <!-- Section: Sprachen -->
                <div>
                  <div class="flex items-center gap-2 mb-3">
                    <div class="h-1 w-4 rounded-full bg-violet-500"></div>
                    <span class="font-mono text-[11px] text-zinc-500 uppercase tracking-widest">Sprachen</span>
                  </div>
                  <div class="ml-6 grid grid-cols-2 gap-2">
                    <div class="flex items-center justify-between">
                      <span class="text-xs text-zinc-400 font-mono">Deutsch</span>
                      <div class="flex gap-0.5">
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                      </div>
                    </div>
                    <div class="flex items-center justify-between">
                      <span class="text-xs text-zinc-400 font-mono">Englisch</span>
                      <div class="flex gap-0.5">
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-violet-500"></div>
                        <div class="h-1.5 w-4 rounded-full bg-zinc-800"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ SOCIAL PROOF ═══════════════════ -->
    <section class="relative py-16 border-y border-white/[0.06]">
      <div class="mx-auto max-w-7xl px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
          <div v-for="stat in [
            { value: '10.000+', label: 'Nutzer' },
            { value: '30+', label: 'Vorlagen' },
            { value: '4.9/5', label: 'Bewertung' },
            { value: '98%', label: 'Zufriedenheit' },
          ]" :key="stat.label" class="text-center">
            <p class="font-mono text-3xl lg:text-4xl font-bold text-foreground">{{ stat.value }}</p>
            <p class="mt-1 text-sm text-zinc-500 font-mono uppercase tracking-wider">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ PRODUCT PREVIEW (terminal split) ═══════════════════ -->
    <section class="relative py-24 lg:py-32">
      <div class="mx-auto max-w-6xl px-6">
        <div class="text-center mb-16 animate-fade-in">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">
            Von der Eingabe zum <span class="text-gradient">PDF in Sekunden</span>
          </h2>
          <p class="mt-4 text-lg text-zinc-400 max-w-2xl mx-auto">
            Intuitiver Editor mit Live-Vorschau. Kein Software-Download, kein Frust.
          </p>
        </div>

        <!-- Terminal-style split panel -->
        <div class="relative animate-fade-in-up">
          <div class="absolute -inset-4 bg-gradient-to-r from-indigo-500/5 via-violet-500/5 to-cyan-500/5 rounded-3xl blur-2xl"></div>

          <div class="relative rounded-2xl border border-white/[0.08] bg-[#0d0d11] overflow-hidden">
            <!-- Terminal header -->
            <div class="flex items-center gap-3 px-5 py-3 border-b border-white/[0.06] bg-[#0a0a0e]">
              <div class="flex gap-1.5">
                <div class="h-3 w-3 rounded-full bg-zinc-700"></div>
                <div class="h-3 w-3 rounded-full bg-zinc-700"></div>
                <div class="h-3 w-3 rounded-full bg-zinc-700"></div>
              </div>
              <div class="flex-1 flex items-center justify-center gap-4">
                <span class="font-mono text-xs text-indigo-400 border-b border-indigo-400 pb-1 px-2">Editor</span>
                <span class="font-mono text-xs text-zinc-600 px-2">Vorschau</span>
                <span class="font-mono text-xs text-zinc-600 px-2">PDF</span>
              </div>
              <div class="font-mono text-xs text-zinc-600 flex items-center gap-1.5">
                <Command class="h-3 w-3" />S gespeichert
              </div>
            </div>

            <!-- Split content -->
            <div class="grid grid-cols-1 md:grid-cols-2 divide-x divide-white/[0.06]">
              <!-- Left: Section list (editor-style) -->
              <div class="p-6 space-y-3">
                <div class="font-mono text-xs text-zinc-600 uppercase tracking-wider mb-4">Abschnitte</div>
                <div v-for="(section, i) in [
                  { name: 'Persoenliche Daten', status: 'complete', color: 'emerald' },
                  { name: 'Berufserfahrung', status: 'complete', color: 'emerald' },
                  { name: 'Ausbildung', status: 'complete', color: 'emerald' },
                  { name: 'Kenntnisse', status: 'editing', color: 'indigo' },
                  { name: 'Sprachen', status: 'pending', color: 'zinc' },
                ]" :key="section.name"
                  :class="[
                    'flex items-center gap-3 px-4 py-3 rounded-xl font-mono text-sm transition-all',
                    section.status === 'editing'
                      ? 'bg-indigo-500/5 border border-indigo-500/20 text-foreground'
                      : 'text-zinc-400 hover:bg-white/[0.02]',
                  ]"
                >
                  <span :class="[
                    'text-[10px]',
                    section.status === 'complete' ? 'text-emerald-500' : section.status === 'editing' ? 'text-indigo-400' : 'text-zinc-600'
                  ]">{{ section.status === 'complete' ? '✓' : section.status === 'editing' ? '›' : '○' }}</span>
                  <span>{{ section.name }}</span>
                  <span v-if="section.status === 'editing'" class="ml-auto text-[10px] text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">bearbeiten</span>
                  <span v-if="i < 3" class="ml-auto text-[10px] text-zinc-600">{{ 3 - i }} Eintrage</span>
                </div>
                <button class="flex items-center gap-2 px-4 py-3 rounded-xl font-mono text-sm text-zinc-600 hover:text-zinc-400 hover:bg-white/[0.02] transition-colors w-full">
                  <span class="text-zinc-600">+</span>
                  Abschnitt hinzufugen
                </button>
              </div>

              <!-- Right: Form preview -->
              <div class="p-6">
                <div class="font-mono text-xs text-zinc-600 uppercase tracking-wider mb-4">Kenntnisse bearbeiten</div>
                <div class="space-y-4">
                  <!-- Skill inputs (mock) -->
                  <div class="flex items-center gap-3">
                    <div class="flex-1 h-10 rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 flex items-center">
                      <span class="font-mono text-sm text-foreground">TypeScript</span>
                    </div>
                    <div class="flex gap-1">
                      <div v-for="j in 5" :key="j" :class="['h-2 w-6 rounded-full', j <= 4 ? 'bg-indigo-500' : 'bg-zinc-800']"></div>
                    </div>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="flex-1 h-10 rounded-lg border border-white/[0.08] bg-white/[0.02] px-3 flex items-center">
                      <span class="font-mono text-sm text-foreground">React / Vue</span>
                    </div>
                    <div class="flex gap-1">
                      <div v-for="j in 5" :key="j" :class="['h-2 w-6 rounded-full', j <= 5 ? 'bg-cyan-500' : 'bg-zinc-800']"></div>
                    </div>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="flex-1 h-10 rounded-lg border border-indigo-500/30 bg-indigo-500/5 px-3 flex items-center">
                      <span class="font-mono text-sm text-foreground cursor-blink">Docker</span>
                    </div>
                    <div class="flex gap-1">
                      <div v-for="j in 5" :key="j" :class="['h-2 w-6 rounded-full', j <= 3 ? 'bg-violet-500' : 'bg-zinc-800']"></div>
                    </div>
                  </div>
                  <button class="flex items-center gap-2 font-mono text-sm text-indigo-400 hover:text-indigo-300 transition-colors mt-2">
                    <span>+</span> Kenntnis hinzufugen
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ FEATURES ═══════════════════ -->
    <section id="features" class="relative py-24 lg:py-32">
      <div class="absolute inset-0 bg-grid opacity-40"></div>

      <div class="relative mx-auto max-w-7xl px-6">
        <div class="text-center mb-16">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">
            Alles was Sie <span class="text-gradient">brauchen</span>
          </h2>
          <p class="mt-4 text-lg text-zinc-400 max-w-2xl mx-auto">
            Professionelle Werkzeuge fur professionelle Bewerbungen.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="group rounded-2xl border border-white/[0.06] bg-card/50 p-7 hover:border-white/[0.1] hover:bg-card/80 transition-all duration-300"
          >
            <div :class="['flex h-12 w-12 items-center justify-center rounded-xl border mb-5', feature.glow, feature.border]">
              <component :is="feature.icon" :class="['h-5 w-5', feature.accent]" />
            </div>
            <h3 class="font-mono text-base font-semibold text-foreground mb-2">{{ feature.title }}</h3>
            <p class="text-sm text-zinc-400 leading-relaxed">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ TEMPLATES ═══════════════════ -->
    <section class="relative py-24 lg:py-32 border-y border-white/[0.06]">
      <div class="mx-auto max-w-7xl px-6">
        <div class="text-center mb-16">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">
            Vorlagen fur <span class="text-gradient">jeden Karriereweg</span>
          </h2>
          <p class="mt-4 text-lg text-zinc-400 max-w-2xl mx-auto">
            30+ professionelle Designs, erstellt von HR-Experten.
          </p>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 lg:gap-5">
          <div
            v-for="tpl in templateCategories"
            :key="tpl.name"
            class="group cursor-pointer"
          >
            <div class="relative rounded-xl border border-white/[0.06] bg-card/50 overflow-hidden transition-all duration-300 hover:border-white/[0.12] hover:bg-card/80">
              <!-- Template thumbnail -->
              <div class="aspect-[210/297] p-4 flex flex-col">
                <!-- Header -->
                <div class="flex items-center gap-2 mb-3">
                  <div :class="['h-5 w-5 rounded-md', tpl.accent, 'opacity-60']"></div>
                  <div class="space-y-1 flex-1">
                    <div class="h-1.5 w-14 bg-zinc-700/50 rounded-full"></div>
                    <div class="h-1 w-10 bg-zinc-800/50 rounded-full"></div>
                  </div>
                </div>
                <!-- Body lines -->
                <div class="flex-1 space-y-2">
                  <div class="h-1 w-full bg-zinc-800/40 rounded-full"></div>
                  <div class="h-1 w-4/5 bg-zinc-800/40 rounded-full"></div>
                  <div class="h-1 w-full bg-zinc-800/40 rounded-full"></div>
                  <div class="h-1 w-3/5 bg-zinc-800/40 rounded-full"></div>
                  <div class="mt-3 h-1 w-full bg-zinc-800/40 rounded-full"></div>
                  <div class="h-1 w-4/5 bg-zinc-800/40 rounded-full"></div>
                  <div class="h-1 w-full bg-zinc-800/40 rounded-full"></div>
                </div>
              </div>

              <!-- Hover overlay -->
              <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-black/40 backdrop-blur-sm transition-all duration-300">
                <span class="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white shadow-lg">
                  Vorlage nutzen
                </span>
              </div>
            </div>
            <div class="mt-2.5 flex items-center justify-center gap-2">
              <span :class="['inline-block px-2 py-0.5 text-[11px] font-mono rounded-md border', tpl.badge]">{{ tpl.name }}</span>
            </div>
          </div>
        </div>

        <div class="mt-12 text-center">
          <RouterLink to="/app/templates" class="inline-flex items-center gap-2 font-mono text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
            Alle Vorlagen entdecken
            <ArrowRight class="h-3.5 w-3.5" />
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ HOW IT WORKS ═══════════════════ -->
    <section class="relative py-24 lg:py-32">
      <div class="mx-auto max-w-7xl px-6">
        <div class="text-center mb-16">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">
            Drei Schritte. <span class="text-gradient">Fertig.</span>
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          <div v-for="(step, i) in steps" :key="step.num" class="relative text-center">
            <!-- Number -->
            <div class="inline-flex h-16 w-16 items-center justify-center rounded-2xl border border-white/[0.08] bg-card font-mono text-2xl font-bold text-indigo-400 mb-6 glow-border">
              {{ step.num }}
            </div>
            <h3 class="font-mono text-lg font-semibold text-foreground">{{ step.title }}</h3>
            <p class="mt-2 text-zinc-400 max-w-xs mx-auto leading-relaxed">{{ step.desc }}</p>

            <!-- Connector (desktop) -->
            <div v-if="i < 2" class="hidden md:block absolute top-8 left-[calc(50%+3.5rem)] w-[calc(100%-7rem)]">
              <div class="h-px bg-gradient-to-r from-indigo-500/30 to-transparent relative">
                <ArrowRight class="absolute -right-2 -top-2 h-4 w-4 text-indigo-500/30" />
              </div>
            </div>
          </div>
        </div>

        <div class="mt-14 text-center">
          <RouterLink to="/register">
            <Button size="lg" class="h-13 px-8 text-base glow-md hover:glow-lg transition-all duration-300">
              Jetzt ausprobieren
              <ArrowRight class="h-4 w-4" />
            </Button>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ TESTIMONIALS ═══════════════════ -->
    <section class="relative py-24 lg:py-32 border-y border-white/[0.06]">
      <div class="absolute inset-0 bg-dots opacity-30"></div>
      <div class="relative mx-auto max-w-7xl px-6">
        <div class="text-center mb-16">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">
            Das sagen <span class="text-gradient">unsere Nutzer</span>
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div
            v-for="t in testimonials"
            :key="t.name"
            class="rounded-2xl border border-white/[0.06] bg-card/50 p-7 hover:border-white/[0.1] transition-colors"
          >
            <div class="flex gap-0.5 mb-5">
              <Star v-for="s in t.rating" :key="s" class="h-4 w-4 text-amber-400 fill-amber-400" />
            </div>
            <p class="text-sm text-zinc-300 leading-relaxed">"{{ t.text }}"</p>
            <div class="mt-6 flex items-center gap-3 pt-5 border-t border-white/[0.06]">
              <div class="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center text-white font-mono font-bold text-sm">
                {{ t.name.charAt(0) }}
              </div>
              <div>
                <p class="text-sm font-semibold text-foreground">{{ t.name }}</p>
                <p class="text-xs text-zinc-500 font-mono">{{ t.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ PRICING ═══════════════════ -->
    <section id="pricing" class="relative py-24 lg:py-32">
      <div class="mx-auto max-w-7xl px-6">
        <div class="text-center mb-16">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">
            Faire <span class="text-gradient">Preise</span>
          </h2>
          <p class="mt-4 text-lg text-zinc-400 max-w-2xl mx-auto">
            Alle Preise inkl. 19% MwSt. Keine versteckten Kosten.
          </p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <PricingCard
            v-for="plan in SUBSCRIPTION_PLANS"
            :key="plan.id"
            :name="plan.name"
            :price="plan.price"
            :period="plan.period"
            :features="plan.features"
            :highlighted="plan.highlighted"
            @select="$router.push('/register')"
          />
        </div>
      </div>
    </section>

    <!-- ═══════════════════ FAQ ═══════════════════ -->
    <section class="relative py-24 lg:py-32 border-t border-white/[0.06]">
      <div class="mx-auto max-w-3xl px-6">
        <div class="text-center mb-16">
          <h2 class="font-mono text-3xl lg:text-4xl font-bold tracking-tight">FAQ</h2>
        </div>

        <div class="space-y-3">
          <div
            v-for="(faq, i) in faqs"
            :key="i"
            class="rounded-xl border border-white/[0.06] bg-card/50 overflow-hidden transition-colors hover:border-white/[0.1]"
          >
            <button
              class="flex items-center justify-between w-full px-6 py-4 text-left text-sm font-medium text-foreground transition-colors"
              @click="toggleFaq(i)"
            >
              <span class="font-mono">{{ faq.q }}</span>
              <ChevronDown
                :class="[
                  'h-4 w-4 text-zinc-500 shrink-0 ml-4 transition-transform duration-200',
                  openFaq === i ? 'rotate-180' : '',
                ]"
              />
            </button>
            <div
              :class="[
                'overflow-hidden transition-all duration-200',
                openFaq === i ? 'max-h-60 opacity-100' : 'max-h-0 opacity-0',
              ]"
            >
              <p class="px-6 pb-5 text-sm text-zinc-400 leading-relaxed">{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════ FINAL CTA ═══════════════════ -->
    <section class="relative py-28 lg:py-36 overflow-hidden">
      <!-- Gradient mesh background -->
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-950 via-[#0d0d11] to-violet-950"></div>
      <div class="absolute inset-0 bg-grid opacity-20"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-indigo-500/10 blur-[150px]"></div>

      <div class="relative mx-auto max-w-3xl px-6 text-center">
        <h2 class="font-mono text-3xl lg:text-5xl font-bold tracking-tight">
          Bereit?
        </h2>
        <p class="mt-5 text-lg text-zinc-400 max-w-xl mx-auto">
          Erstellen Sie jetzt Ihren professionellen Lebenslauf. Kostenlos.
        </p>
        <div class="mt-10">
          <RouterLink to="/register">
            <Button size="lg" class="h-14 px-10 text-lg glow-lg hover:scale-[1.02] transition-all duration-300">
              Lebenslauf erstellen
              <ArrowRight class="h-5 w-5" />
            </Button>
          </RouterLink>
        </div>
        <p class="mt-6 text-sm text-zinc-500 font-mono flex items-center justify-center gap-2">
          <CheckCircle2 class="h-4 w-4 text-emerald-500" />
          Kostenlos. Keine Kreditkarte.
        </p>
      </div>
    </section>

    <!-- ═══════════════════ FOOTER ═══════════════════ -->
    <footer class="border-t border-white/[0.06] py-14">
      <div class="mx-auto max-w-7xl px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <!-- Brand -->
          <div class="col-span-2 md:col-span-1">
            <RouterLink to="/" class="flex items-center gap-2.5">
              <div class="flex h-7 w-7 items-center justify-center rounded-md bg-indigo-500/10 border border-indigo-500/20 font-mono text-xs font-bold text-indigo-400">&gt;_</div>
              <span class="text-base font-semibold text-foreground">GetResume</span>
            </RouterLink>
            <p class="mt-3 text-sm text-zinc-500 leading-relaxed">
              Professionelle Lebensläufe fur den deutschen Arbeitsmarkt. DSGVO-konform.
            </p>
          </div>

          <!-- Product -->
          <div>
            <h4 class="text-xs font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-4">Produkt</h4>
            <ul class="space-y-2.5 text-sm text-zinc-500">
              <li><RouterLink to="/app/templates" class="hover:text-foreground transition-colors">Vorlagen</RouterLink></li>
              <li><RouterLink to="/preise" class="hover:text-foreground transition-colors">Preise</RouterLink></li>
              <li><a href="#features" class="hover:text-foreground transition-colors">Features</a></li>
            </ul>
          </div>

          <!-- Resources -->
          <div>
            <h4 class="text-xs font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-4">Ressourcen</h4>
            <ul class="space-y-2.5 text-sm text-zinc-500">
              <li><a href="#" class="hover:text-foreground transition-colors">Karriere-Blog</a></li>
              <li><a href="#" class="hover:text-foreground transition-colors">Lebenslauf-Tipps</a></li>
            </ul>
          </div>

          <!-- Legal -->
          <div>
            <h4 class="text-xs font-mono font-semibold text-zinc-400 uppercase tracking-wider mb-4">Rechtliches</h4>
            <ul class="space-y-2.5 text-sm text-zinc-500">
              <li><RouterLink to="/impressum" class="hover:text-foreground transition-colors">Impressum</RouterLink></li>
              <li><RouterLink to="/datenschutz" class="hover:text-foreground transition-colors">Datenschutz</RouterLink></li>
              <li><RouterLink to="/agb" class="hover:text-foreground transition-colors">AGB</RouterLink></li>
            </ul>
          </div>
        </div>

        <!-- Bottom -->
        <div class="mt-12 pt-6 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-3">
          <p class="text-xs text-zinc-600 font-mono">&copy; 2026 GetResume GmbH</p>
          <div class="flex items-center gap-4 text-xs text-zinc-600 font-mono">
            <span class="flex items-center gap-1.5">
              <Shield class="h-3 w-3 text-emerald-500" />
              DSGVO
            </span>
            <span class="flex items-center gap-1.5">
              <Lock class="h-3 w-3 text-emerald-500" />
              SSL
            </span>
            <span class="flex items-center gap-1.5">
              <Code2 class="h-3 w-3 text-indigo-400" />
              Made in Germany
            </span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.dropdown-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
