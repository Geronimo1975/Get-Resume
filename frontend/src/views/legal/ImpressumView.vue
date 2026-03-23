<template>
  <div class="min-h-screen bg-background">
    <div class="mx-auto max-w-3xl px-6 py-16">
      <h1 class="font-mono text-3xl font-bold text-foreground mb-8">Impressum</h1>

      <div class="max-w-none space-y-6 text-zinc-300">
        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">Angaben gemafl &sect;5 TMG</h2>
          <p>
            GetResume GmbH<br />
            Musterstrafl e 123<br />
            10115 Berlin<br />
            Deutschland
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">Vertreten durch</h2>
          <p>Geschaftsfuhrer: [Name eintragen]</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">Kontakt</h2>
          <p>
            Telefon: +49 (0) 30 123456-0<br />
            E-Mail: info@getresume.de
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">Registereintrag</h2>
          <p>
            Eintragung im Handelsregister.<br />
            Registergericht: Amtsgericht Berlin-Charlottenburg<br />
            Registernummer: HRB [Nummer eintragen]
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">Umsatzsteuer-ID</h2>
          <p>
            Umsatzsteuer-Identifikationsnummer gemafl &sect;27a Umsatzsteuergesetz:<br />
            DE [Nummer eintragen]
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">Verantwortlich fur den Inhalt nach &sect;55 Abs. 2 RStV</h2>
          <p>
            [Name eintragen]<br />
            Musterstrafl e 123<br />
            10115 Berlin
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">EU-Streitschlichtung</h2>
          <p class="text-sm text-muted-foreground">
            Die Europaische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
            <a href="https://ec.europa.eu/consumers/odr/" class="text-primary-600 hover:underline" target="_blank" rel="noopener">
              https://ec.europa.eu/consumers/odr/
            </a>.<br />
            Unsere E-Mail-Adresse finden Sie oben im Impressum.
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
            Verbraucherschlichtungsstelle teilzunehmen.
          </p>
        </section>
      </div>

      <div class="mt-12">
        <RouterLink to="/" class="text-sm text-primary-600 hover:underline">&larr; Zuruck zur Startseite</RouterLink>
      </div>
    </div>
  </div>
</template>
