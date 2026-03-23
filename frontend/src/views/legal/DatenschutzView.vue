<template>
  <div class="min-h-screen bg-background">
    <div class="mx-auto max-w-3xl px-6 py-16">
      <h1 class="font-mono text-3xl font-bold text-foreground mb-8">Datenschutzerklarung</h1>

      <div class="max-w-none space-y-6 text-zinc-300 text-sm leading-relaxed">
        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">1. Datenschutz auf einen Blick</h2>
          <h3 class="text-lg font-medium mt-4 mb-2">Allgemeine Hinweise</h3>
          <p>Die folgenden Hinweise geben einen einfachen Uberblick daruber, was mit Ihren personenbezogenen Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit denen Sie personlich identifiziert werden konnen.</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">2. Verantwortliche Stelle</h2>
          <p>
            GetResume GmbH<br />
            Musterstrafl e 123<br />
            10115 Berlin<br />
            E-Mail: datenschutz@getresume.de
          </p>
          <p>Verantwortliche Stelle ist die naturliche oder juristische Person, die allein oder gemeinsam mit anderen uber die Zwecke und Mittel der Verarbeitung von personenbezogenen Daten entscheidet.</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">3. Datenerfassung auf dieser Website</h2>

          <h3 class="text-lg font-medium mt-4 mb-2">Cookies</h3>
          <p>Unsere Internetseiten verwenden sogenannte Cookies. Cookies sind kleine Datenpakete und richten auf Ihrem Endgerat keinen Schaden an. Sie werden entweder vorubergehend fur die Dauer einer Sitzung (Session-Cookies) oder dauerhaft (permanente Cookies) auf Ihrem Endgerat gespeichert.</p>
          <p>Gemafl &sect;25 TTDSG holen wir Ihre Einwilligung ein, bevor nicht-essenzielle Cookies gesetzt werden.</p>

          <h3 class="text-lg font-medium mt-4 mb-2">Server-Log-Dateien</h3>
          <p>Der Provider der Seiten erhebt und speichert automatisch Informationen in sogenannten Server-Log-Dateien, die Ihr Browser automatisch an uns ubermittelt. Dies sind: Browsertyp und Browserversion, verwendetes Betriebssystem, Referrer URL, Hostname des zugreifenden Rechners, Uhrzeit der Serveranfrage, IP-Adresse.</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">4. Registrierung und Nutzerkonto</h2>
          <p>Bei der Registrierung verarbeiten wir folgende Daten: E-Mail-Adresse, Vorname, Nachname, Passwort (verschlusselt gespeichert). Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Vertragserffullung).</p>
          <p>Im Rahmen der Profilnutzung konnen Sie freiwillig weitere Daten angeben: Anrede, Geburtsdatum, Telefonnummer, Adresse, Bundesland. Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO (Einwilligung).</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">5. Ihre Rechte nach DSGVO</h2>
          <ul class="list-disc pl-6 space-y-1">
            <li><strong>Auskunft (Art. 15 DSGVO)</strong>: Sie konnen Auskunft uber Ihre bei uns gespeicherten personenbezogenen Daten verlangen.</li>
            <li><strong>Berichtigung (Art. 16 DSGVO)</strong>: Sie konnen die Berichtigung unrichtiger Daten verlangen.</li>
            <li><strong>Loschung (Art. 17 DSGVO)</strong>: Sie konnen die Loschung Ihrer Daten verlangen. Nutzen Sie hierzu die Funktion in den Einstellungen.</li>
            <li><strong>Einschrankung (Art. 18 DSGVO)</strong>: Sie konnen die Einschrankung der Verarbeitung verlangen.</li>
            <li><strong>Datenubertragbarkeit (Art. 20 DSGVO)</strong>: Sie konnen Ihre Daten in einem maschinenlesbaren Format anfordern. Nutzen Sie hierzu die Export-Funktion in den Einstellungen.</li>
            <li><strong>Widerspruch (Art. 21 DSGVO)</strong>: Sie konnen der Verarbeitung Ihrer Daten widersprechen.</li>
            <li><strong>Widerruf (Art. 7 Abs. 3 DSGVO)</strong>: Sie konnen Ihre Einwilligung jederzeit widerrufen.</li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">6. Datensicherheit</h2>
          <p>Wir verwenden SSL- bzw. TLS-Verschlusselung aus Sicherheitsgrunden und zum Schutz der Ubertragung vertraulicher Inhalte. Passworter werden mit bcrypt gehasht und niemals im Klartext gespeichert.</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">7. Zahlungsabwicklung</h2>
          <p>Zahlungen werden uber Stripe Inc. abgewickelt. Stripe verarbeitet Zahlungsdaten in Ubereinstimmung mit PCI DSS Level 1. Wir speichern keine Kreditkartendaten. Datenschutzerklarung von Stripe: <a href="https://stripe.com/de/privacy" class="text-primary-600 hover:underline" target="_blank" rel="noopener">stripe.com/de/privacy</a></p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mt-8 mb-3">8. Hosting</h2>
          <p>Diese Website wird bei Amazon Web Services (AWS) in der Region EU (Frankfurt, eu-central-1) gehostet. Auftragsverarbeitungsvertrag (AVV) gemafl Art. 28 DSGVO liegt vor.</p>
        </section>
      </div>

      <div class="mt-12">
        <RouterLink to="/" class="text-sm text-primary-600 hover:underline">&larr; Zuruck zur Startseite</RouterLink>
      </div>
    </div>
  </div>
</template>
