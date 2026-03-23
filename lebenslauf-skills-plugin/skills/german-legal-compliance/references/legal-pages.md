# Legal Pages Reference

Complete Django HTML templates for all legally required pages under German law.

---

## URL Configuration

```python
# legal/urls.py

from django.urls import path
from . import views

app_name = "legal"

urlpatterns = [
    # Legal pages (static content)
    path("impressum/", views.ImpressumView.as_view(), name="impressum"),
    path("datenschutz/", views.DatenschutzView.as_view(), name="datenschutz"),
    path("agb/", views.AGBView.as_view(), name="agb"),
    path("widerrufsbelehrung/", views.WiderrufsbelehrungView.as_view(), name="widerrufsbelehrung"),

    # Cookie consent (HTMX endpoints)
    path("cookie-consent/", views.CookieBannerView.as_view(), name="cookie_banner"),
    path("cookie-consent/save/", views.CookieConsentSaveView.as_view(), name="cookie_consent_save"),
    path("cookie-consent/settings/", views.CookieSettingsView.as_view(), name="cookie_settings"),
    path("cookie-consent/details/", views.CookieDetailsView.as_view(), name="cookie_details"),
    path("cookie-consent/revoke/", views.CookieConsentRevokeView.as_view(), name="cookie_consent_revoke"),

    # GDPR user rights
    path("meine-daten/", views.DataAccessView.as_view(), name="data_access"),
    path("meine-daten/export/", views.DataExportView.as_view(), name="data_export"),
    path("meine-daten/loeschen/", views.DataDeletionView.as_view(), name="data_deletion"),
]
```

---

## Views

```python
# legal/views.py

from django.views.generic import TemplateView


class ImpressumView(TemplateView):
    template_name = "legal/impressum.html"


class DatenschutzView(TemplateView):
    template_name = "legal/datenschutz.html"


class AGBView(TemplateView):
    template_name = "legal/agb.html"


class WiderrufsbelehrungView(TemplateView):
    template_name = "legal/widerrufsbelehrung.html"
```

---

## 1. Impressum (TMG 5 / DDG Art. 5)

Must be accessible within 2 clicks from ANY page. Link labeled "Impressum" in footer.

```html
{# templates/legal/impressum.html #}

{% extends "base.html" %}
{% load i18n %}

{% block title %}Impressum | Lebenslauf-Builder{% endblock %}

{% block meta_description %}Impressum der Lebenslauf-Builder GmbH gemaess TMG §5.{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto px-4 py-12">

  <h1 class="text-3xl font-bold mb-8">Impressum</h1>

  <p class="text-sm text-gray-500 mb-6">
    Angaben gemäß § 5 TMG / Art. 5 DDG
  </p>

  {# ── Company Information ──────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Angaben zum Diensteanbieter</h2>
    <address class="not-italic leading-relaxed">
      <strong>Lebenslauf-Builder GmbH</strong><br>
      Musterstraße 123<br>
      10115 Berlin<br>
      Deutschland
    </address>
  </section>

  {# ── Legal Representation ─────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Vertreten durch</h2>
    <p>Geschäftsführer: Max Mustermann</p>
  </section>

  {# ── Contact Information (2 methods required) ─── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Kontakt</h2>
    <table class="text-left">
      <tr>
        <td class="pr-4 py-1 font-medium">E-Mail:</td>
        <td><a href="mailto:info@lebenslauf-builder.de" class="text-blue-600 hover:underline">info@lebenslauf-builder.de</a></td>
      </tr>
      <tr>
        <td class="pr-4 py-1 font-medium">Telefon:</td>
        <td><a href="tel:+4930123456789">+49 (0) 30 123 456 789</a></td>
      </tr>
    </table>
  </section>

  {# ── Commercial Register ──────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Handelsregister</h2>
    <table class="text-left">
      <tr>
        <td class="pr-4 py-1 font-medium">Registergericht:</td>
        <td>Amtsgericht Berlin-Charlottenburg</td>
      </tr>
      <tr>
        <td class="pr-4 py-1 font-medium">Registernummer:</td>
        <td>HRB 123456 B</td>
      </tr>
    </table>
  </section>

  {# ── Tax Information ──────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Umsatzsteuer</h2>
    <table class="text-left">
      <tr>
        <td class="pr-4 py-1 font-medium">USt-IdNr.:</td>
        <td>DE123456789</td>
      </tr>
      <tr>
        <td class="pr-4 py-1 font-medium">Steuernummer:</td>
        <td>27/123/45678</td>
      </tr>
    </table>
  </section>

  {# ── Responsible for Content ──────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2>
    <p>
      Max Mustermann<br>
      Musterstraße 123<br>
      10115 Berlin
    </p>
  </section>

  {# ── EU Dispute Resolution ────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">EU-Streitschlichtung</h2>
    <p class="mb-2">
      Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
    </p>
    <p class="mb-2">
      <a href="https://ec.europa.eu/consumers/odr" target="_blank" rel="noopener noreferrer"
         class="text-blue-600 hover:underline">
        https://ec.europa.eu/consumers/odr
      </a>
    </p>
    <p>
      Unsere E-Mail-Adresse finden Sie oben im Impressum.
    </p>
  </section>

  {# ── Alternative Dispute Resolution ───────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Verbraucherstreitbeilegung / Universalschlichtungsstelle</h2>
    <p>
      Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
      Verbraucherschlichtungsstelle teilzunehmen.
    </p>
  </section>

  {# ── Liability Notice ─────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Haftung für Inhalte</h2>
    <p class="mb-2">
      Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf diesen Seiten
      nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als
      Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde
      Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige
      Tätigkeit hinweisen.
    </p>
    <p>
      Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den
      allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch
      erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei
      Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend
      entfernen.
    </p>
  </section>

  {# ── Link Liability ───────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Haftung für Links</h2>
    <p>
      Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen
      Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen.
      Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der
      Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf
      mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der
      Verlinkung nicht erkennbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige
      Links umgehend entfernen.
    </p>
  </section>

  {# ── Copyright ─────────────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Urheberrecht</h2>
    <p>
      Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen
      dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art
      der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen
      Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind
      nur für den privaten, nicht kommerziellen Gebrauch gestattet.
    </p>
  </section>

</div>
{% endblock %}
```

---

## 2. Datenschutzerklaerung (Art. 13/14 DSGVO)

```html
{# templates/legal/datenschutz.html #}

{% extends "base.html" %}
{% load i18n %}

{% block title %}Datenschutzerklärung | Lebenslauf-Builder{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto px-4 py-12">

  <h1 class="text-3xl font-bold mb-4">Datenschutzerklärung</h1>
  <p class="text-sm text-gray-500 mb-8">Stand: {{ current_date|default:"01.03.2026" }}</p>

  {# ── Table of Contents ─────────────────────────── #}
  <nav class="mb-10 p-4 bg-gray-50 rounded-lg">
    <h2 class="font-semibold mb-3">Inhaltsverzeichnis</h2>
    <ol class="list-decimal list-inside space-y-1 text-sm text-blue-600">
      <li><a href="#verantwortlicher">Verantwortlicher</a></li>
      <li><a href="#dsb">Datenschutzbeauftragter</a></li>
      <li><a href="#uebersicht">Übersicht der Verarbeitungen</a></li>
      <li><a href="#registrierung">Registrierung und Nutzerkonto</a></li>
      <li><a href="#dokumente">Dokumentenerstellung</a></li>
      <li><a href="#zahlung">Zahlungsabwicklung (Stripe)</a></li>
      <li><a href="#cookies">Cookies und Tracking</a></li>
      <li><a href="#email">E-Mail-Versand</a></li>
      <li><a href="#hosting">Hosting und CDN</a></li>
      <li><a href="#rechte">Betroffenenrechte</a></li>
      <li><a href="#beschwerde">Beschwerderecht</a></li>
      <li><a href="#aenderungen">Änderungen</a></li>
    </ol>
  </nav>

  {# ── 1. Verantwortlicher ───────────────────────── #}
  <section id="verantwortlicher" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">1. Verantwortlicher</h2>
    <p class="mb-2">Verantwortlich im Sinne der DSGVO:</p>
    <address class="not-italic leading-relaxed mb-4">
      Lebenslauf-Builder GmbH<br>
      Musterstraße 123<br>
      10115 Berlin<br>
      E-Mail: datenschutz@lebenslauf-builder.de<br>
      Telefon: +49 (0) 30 123 456 789
    </address>
  </section>

  {# ── 2. Datenschutzbeauftragter ────────────────── #}
  <section id="dsb" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">2. Datenschutzbeauftragter</h2>
    <p>
      {# Only required if >20 employees process personal data regularly #}
      Unseren Datenschutzbeauftragten erreichen Sie unter:<br>
      <a href="mailto:datenschutz@lebenslauf-builder.de" class="text-blue-600 hover:underline">
        datenschutz@lebenslauf-builder.de
      </a>
    </p>
  </section>

  {# ── 3. Übersicht der Verarbeitungen ───────────── #}
  <section id="uebersicht" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">3. Übersicht der Verarbeitungen</h2>
    <p class="mb-4">Die nachfolgende Übersicht fasst die Arten der verarbeiteten Daten und die Zwecke ihrer Verarbeitung zusammen:</p>

    <h3 class="font-semibold mb-2">Arten der verarbeiteten Daten</h3>
    <ul class="list-disc list-inside mb-4 space-y-1">
      <li>Bestandsdaten (Name, Adresse, Geburtsdatum)</li>
      <li>Kontaktdaten (E-Mail, Telefon)</li>
      <li>Inhaltsdaten (Lebenslauf-Inhalte, Dokumente)</li>
      <li>Nutzungsdaten (Seitenaufrufe, Zugriffszeiten)</li>
      <li>Vertragsdaten (Abonnement, Zahlungsinformationen)</li>
      <li>Meta-/Kommunikationsdaten (IP-Adresse, User-Agent)</li>
    </ul>

    <h3 class="font-semibold mb-2">Rechtsgrundlagen</h3>
    <ul class="list-disc list-inside mb-4 space-y-1">
      <li><strong>Einwilligung (Art. 6 Abs. 1 lit. a DSGVO)</strong> — Cookies, Newsletter, Marketing</li>
      <li><strong>Vertragserfüllung (Art. 6 Abs. 1 lit. b DSGVO)</strong> — Nutzerkonto, Dokumentenerstellung, Zahlung</li>
      <li><strong>Rechtliche Verpflichtung (Art. 6 Abs. 1 lit. c DSGVO)</strong> — Rechnungsaufbewahrung (AO §147)</li>
      <li><strong>Berechtigtes Interesse (Art. 6 Abs. 1 lit. f DSGVO)</strong> — Sicherheit, Missbrauchsverhinderung</li>
    </ul>
  </section>

  {# ── 4. Registrierung ─────────────────────────── #}
  <section id="registrierung" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">4. Registrierung und Nutzerkonto</h2>
    <table class="w-full text-sm border-collapse mb-4">
      <tr class="border-b"><td class="py-2 pr-4 font-medium w-1/3">Zweck</td><td>Bereitstellung eines Nutzerkontos zur Dokumentenerstellung</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Verarbeitete Daten</td><td>E-Mail, Name, Passwort (gehasht), IP-Adresse bei Registrierung</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Rechtsgrundlage</td><td>Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Speicherdauer</td><td>Bis zur Kontolöschung durch den Nutzer, danach 30 Tage Soft-Delete</td></tr>
      <tr><td class="py-2 pr-4 font-medium">Empfänger</td><td>Keine Weitergabe an Dritte</td></tr>
    </table>
  </section>

  {# ── 5. Dokumentenerstellung ───────────────────── #}
  <section id="dokumente" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">5. Dokumentenerstellung</h2>
    <table class="w-full text-sm border-collapse mb-4">
      <tr class="border-b"><td class="py-2 pr-4 font-medium w-1/3">Zweck</td><td>Erstellung, Speicherung und PDF-Export von Lebensläufen</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Verarbeitete Daten</td><td>Persönliche Daten im Lebenslauf (Name, Adresse, Berufserfahrung, Foto)</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Rechtsgrundlage</td><td>Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Speicherdauer</td><td>Bis zur Löschung durch den Nutzer</td></tr>
      <tr><td class="py-2 pr-4 font-medium">Hinweis</td><td>CV-Daten werden ausschließlich auf Servern in Deutschland (Hetzner, Falkenstein) gespeichert</td></tr>
    </table>
  </section>

  {# ── 6. Zahlungsabwicklung ─────────────────────── #}
  <section id="zahlung" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">6. Zahlungsabwicklung (Stripe)</h2>
    <table class="w-full text-sm border-collapse mb-4">
      <tr class="border-b"><td class="py-2 pr-4 font-medium w-1/3">Zweck</td><td>Abwicklung von Abonnement-Zahlungen</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Verarbeitete Daten</td><td>E-Mail, Name, Zahlungsinformationen (via Stripe — nicht bei uns gespeichert)</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Rechtsgrundlage</td><td>Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Empfänger</td><td>Stripe Payments Europe, Ltd., 1 Grand Canal Street Lower, Dublin, Irland</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Drittlandtransfer</td><td>EU-Standardvertragsklauseln (Stripe verarbeitet Daten in der EU)</td></tr>
      <tr><td class="py-2 pr-4 font-medium">Datenschutz Stripe</td><td><a href="https://stripe.com/de/privacy" class="text-blue-600 hover:underline" target="_blank" rel="noopener">stripe.com/de/privacy</a></td></tr>
    </table>
    <p class="text-sm">
      <strong>Hinweis:</strong> Kreditkartendaten und Bankverbindungen werden ausschließlich durch
      Stripe verarbeitet und zu keinem Zeitpunkt auf unseren Servern gespeichert.
    </p>
  </section>

  {# ── 7. Cookies ────────────────────────────────── #}
  <section id="cookies" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">7. Cookies und Tracking</h2>
    <p class="mb-4">
      Wir setzen Cookies und ähnliche Technologien ein, um unsere Website bereitzustellen.
      Nicht notwendige Cookies werden nur mit Ihrer ausdrücklichen Einwilligung gesetzt
      (§ 25 TTDSG, Art. 6 Abs. 1 lit. a DSGVO).
    </p>

    <h3 class="font-semibold mb-2">Notwendige Cookies</h3>
    <div class="overflow-x-auto mb-4">
      <table class="w-full text-sm border border-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="p-2 text-left border-b">Name</th>
            <th class="p-2 text-left border-b">Anbieter</th>
            <th class="p-2 text-left border-b">Zweck</th>
            <th class="p-2 text-left border-b">Ablauf</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-b">
            <td class="p-2"><code>sessionid</code></td>
            <td class="p-2">Lebenslauf-Builder</td>
            <td class="p-2">Sitzungsverwaltung</td>
            <td class="p-2">24 Stunden</td>
          </tr>
          <tr class="border-b">
            <td class="p-2"><code>csrftoken</code></td>
            <td class="p-2">Lebenslauf-Builder</td>
            <td class="p-2">CSRF-Schutz</td>
            <td class="p-2">1 Jahr</td>
          </tr>
          <tr class="border-b">
            <td class="p-2"><code>cookie_consent</code></td>
            <td class="p-2">Lebenslauf-Builder</td>
            <td class="p-2">Speicherung Ihrer Cookie-Einstellungen</td>
            <td class="p-2">1 Jahr</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h3 class="font-semibold mb-2">Statistik-Cookies (nur mit Einwilligung)</h3>
    <div class="overflow-x-auto mb-4">
      <table class="w-full text-sm border border-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="p-2 text-left border-b">Name</th>
            <th class="p-2 text-left border-b">Anbieter</th>
            <th class="p-2 text-left border-b">Zweck</th>
            <th class="p-2 text-left border-b">Ablauf</th>
          </tr>
        </thead>
        <tbody>
          <tr class="border-b">
            <td class="p-2"><code>_pk_id</code></td>
            <td class="p-2">Matomo (self-hosted)</td>
            <td class="p-2">Nutzer-Identifikation fuer Statistiken</td>
            <td class="p-2">13 Monate</td>
          </tr>
          <tr>
            <td class="p-2"><code>_pk_ses</code></td>
            <td class="p-2">Matomo (self-hosted)</td>
            <td class="p-2">Sitzungsdaten fuer Statistiken</td>
            <td class="p-2">30 Minuten</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="text-sm mb-4">
      Sie können Ihre Cookie-Einstellungen jederzeit über den Link
      <a href="#" onclick="document.getElementById('cookie-banner').classList.remove('hidden'); return false;"
         class="text-blue-600 hover:underline">Cookie-Einstellungen ändern</a>
      anpassen.
    </p>
  </section>

  {# ── 8. E-Mail-Versand ─────────────────────────── #}
  <section id="email" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">8. E-Mail-Versand</h2>
    <table class="w-full text-sm border-collapse mb-4">
      <tr class="border-b"><td class="py-2 pr-4 font-medium w-1/3">Zweck</td><td>Transaktionale E-Mails (Bestätigungen, Rechnungen) und Newsletter</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Dienstleister</td><td>Amazon Web Services EMEA SARL (AWS SES), Region eu-central-1 (Frankfurt)</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Rechtsgrundlage</td><td>Art. 6 Abs. 1 lit. b (transaktional) / lit. a (Newsletter)</td></tr>
      <tr><td class="py-2 pr-4 font-medium">Widerruf Newsletter</td><td>Jederzeit per Abmelde-Link in jeder E-Mail</td></tr>
    </table>
  </section>

  {# ── 9. Hosting ────────────────────────────────── #}
  <section id="hosting" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">9. Hosting</h2>
    <table class="w-full text-sm border-collapse mb-4">
      <tr class="border-b"><td class="py-2 pr-4 font-medium w-1/3">Hoster</td><td>Hetzner Online GmbH, Industriestr. 25, 91710 Gunzenhausen</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Standort</td><td>Falkenstein/Vogtl., Deutschland</td></tr>
      <tr class="border-b"><td class="py-2 pr-4 font-medium">Rechtsgrundlage</td><td>Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse) + AV-Vertrag</td></tr>
      <tr><td class="py-2 pr-4 font-medium">Verarbeitete Daten</td><td>IP-Adresse, Zugriffszeit, angeforderte URL (Server-Logfiles, 7 Tage)</td></tr>
    </table>
  </section>

  {# ── 10. Betroffenenrechte (Art. 15-22 DSGVO) ─── #}
  <section id="rechte" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">10. Ihre Rechte als betroffene Person</h2>
    <p class="mb-4">Ihnen stehen folgende Rechte gemäß DSGVO zu:</p>
    <ul class="space-y-3 mb-4">
      <li>
        <strong>Auskunftsrecht (Art. 15 DSGVO):</strong>
        Sie haben das Recht, Auskunft über Ihre bei uns gespeicherten Daten zu erhalten.
        <a href="{% url 'legal:data_access' %}" class="text-blue-600 hover:underline">Datenauskunft anfordern</a>
      </li>
      <li>
        <strong>Recht auf Berichtigung (Art. 16 DSGVO):</strong>
        Sie können unrichtige Daten jederzeit in Ihrem Profil korrigieren.
      </li>
      <li>
        <strong>Recht auf Löschung (Art. 17 DSGVO):</strong>
        Sie können die Löschung Ihrer Daten verlangen, sofern keine gesetzliche Aufbewahrungspflicht entgegensteht.
        <a href="{% url 'legal:data_deletion' %}" class="text-blue-600 hover:underline">Datenlöschung beantragen</a>
      </li>
      <li>
        <strong>Recht auf Einschränkung (Art. 18 DSGVO):</strong>
        Sie können die Einschränkung der Verarbeitung Ihrer Daten verlangen.
      </li>
      <li>
        <strong>Recht auf Datenübertragbarkeit (Art. 20 DSGVO):</strong>
        Sie können Ihre Daten in einem strukturierten, gängigen, maschinenlesbaren Format erhalten.
        <a href="{% url 'legal:data_export' %}" class="text-blue-600 hover:underline">Datenexport anfordern</a>
      </li>
      <li>
        <strong>Widerspruchsrecht (Art. 21 DSGVO):</strong>
        Sie haben das Recht, der Verarbeitung Ihrer Daten auf Grundlage berechtigter Interessen zu widersprechen.
      </li>
      <li>
        <strong>Recht auf Widerruf der Einwilligung (Art. 7 Abs. 3 DSGVO):</strong>
        Erteilte Einwilligungen können jederzeit mit Wirkung für die Zukunft widerrufen werden.
      </li>
    </ul>
    <p>
      Zur Ausübung Ihrer Rechte wenden Sie sich bitte an:
      <a href="mailto:datenschutz@lebenslauf-builder.de" class="text-blue-600 hover:underline">
        datenschutz@lebenslauf-builder.de
      </a>
    </p>
  </section>

  {# ── 11. Beschwerderecht ───────────────────────── #}
  <section id="beschwerde" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">11. Beschwerderecht bei der Aufsichtsbehörde</h2>
    <p class="mb-2">
      Wenn Sie der Ansicht sind, dass die Verarbeitung Ihrer Daten gegen die DSGVO verstößt,
      haben Sie das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren
      (Art. 77 DSGVO).
    </p>
    <p>
      Zuständige Aufsichtsbehörde:<br>
      Berliner Beauftragte für Datenschutz und Informationsfreiheit<br>
      Alt-Moabit 59-61, 10555 Berlin<br>
      <a href="https://www.datenschutz-berlin.de" target="_blank" rel="noopener noreferrer"
         class="text-blue-600 hover:underline">www.datenschutz-berlin.de</a>
    </p>
  </section>

  {# ── 12. Änderungen ────────────────────────────── #}
  <section id="aenderungen" class="mb-10">
    <h2 class="text-2xl font-semibold mb-3">12. Änderungen dieser Datenschutzerklärung</h2>
    <p>
      Wir behalten uns vor, diese Datenschutzerklärung bei Bedarf anzupassen, um sie an
      geänderte Rechtslagen oder bei Änderungen des Dienstes anzupassen. Für Ihren nächsten
      Besuch gilt die neue Datenschutzerklärung. Wesentliche Änderungen teilen wir per E-Mail mit.
    </p>
  </section>

</div>
{% endblock %}
```

---

## 3. AGB (Allgemeine Geschaeftsbedingungen)

```html
{# templates/legal/agb.html #}

{% extends "base.html" %}
{% load i18n %}

{% block title %}Allgemeine Geschäftsbedingungen | Lebenslauf-Builder{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto px-4 py-12">

  <h1 class="text-3xl font-bold mb-4">Allgemeine Geschäftsbedingungen (AGB)</h1>
  <p class="text-sm text-gray-500 mb-8">Stand: 01.03.2026</p>

  {# ── §1 Geltungsbereich ────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 1 Geltungsbereich</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Diese Allgemeinen Geschäftsbedingungen (nachfolgend „AGB") gelten für alle Verträge
        zwischen der Lebenslauf-Builder GmbH, Musterstraße 123, 10115 Berlin (nachfolgend
        „Anbieter") und dem Nutzer (nachfolgend „Kunde"), die über die Website
        lebenslauf-builder.de geschlossen werden.
      </li>
      <li>
        Maßgeblich ist die zum Zeitpunkt des Vertragsschlusses gültige Fassung der AGB.
      </li>
      <li>
        Abweichende Bedingungen des Kunden werden nicht anerkannt, es sei denn, der Anbieter
        stimmt ihrer Geltung ausdrücklich schriftlich zu.
      </li>
    </ol>
  </section>

  {# ── §2 Vertragsgegenstand ─────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 2 Vertragsgegenstand</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Gegenstand des Vertrages ist die Bereitstellung einer webbasierten
        Software-as-a-Service (SaaS) Plattform zur Erstellung von Lebensläufen,
        Bewerbungsschreiben und Deckblättern.
      </li>
      <li>
        Der Leistungsumfang richtet sich nach dem jeweils gewählten Abonnement-Plan
        (Kostenlos, Premium Monatlich, Premium Jährlich, Business).
      </li>
      <li>
        Der Anbieter stellt die Plattform mit einer Verfügbarkeit von mindestens 99,0%
        im Jahresmittel zur Verfügung. Geplante Wartungsarbeiten werden mindestens 48 Stunden
        vorher angekündigt.
      </li>
    </ol>
  </section>

  {# ── §3 Vertragsschluss ────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 3 Vertragsschluss</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Die Darstellung der Abonnement-Pläne auf der Website stellt kein rechtsverbindliches
        Angebot dar, sondern eine Aufforderung zur Abgabe eines Angebots (invitatio ad offerendum).
      </li>
      <li>
        Durch Klicken des Buttons „Jetzt kostenpflichtig bestellen" gibt der Kunde ein
        verbindliches Angebot zum Abschluss eines Abonnementvertrags ab.
      </li>
      <li>
        Der Vertrag kommt mit der Bestätigungs-E-Mail des Anbieters zustande.
      </li>
    </ol>
  </section>

  {# ── §4 Preise und Zahlung (PAngV compliant) ──── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 4 Preise und Zahlung</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Alle auf der Website angegebenen Preise verstehen sich als Bruttopreise
        <strong>inklusive der gesetzlichen Mehrwertsteuer</strong> von derzeit 19%
        (§ 1 PAngV).
      </li>
      <li>
        Es gelten die zum Zeitpunkt der Bestellung angezeigten Preise:
        <ul class="list-disc list-inside ml-6 mt-2 space-y-1">
          <li>Premium Monatlich: 9,99 EUR/Monat inkl. MwSt (8,40 EUR netto zzgl. 1,59 EUR MwSt)</li>
          <li>Premium Jährlich: 95,88 EUR/Jahr inkl. MwSt (entspricht 7,99 EUR/Monat)</li>
          <li>Business: 19,99 EUR/Monat inkl. MwSt</li>
        </ul>
      </li>
      <li>
        Die Zahlung erfolgt per Kreditkarte, SEPA-Lastschrift, PayPal, Sofortüberweisung
        oder Giropay über den Zahlungsdienstleister Stripe.
      </li>
      <li>
        Rechnungen werden in elektronischer Form (PDF) im Kundenkonto bereitgestellt und
        per E-Mail zugesandt.
      </li>
    </ol>
  </section>

  {# ── §5 Widerrufsrecht ─────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 5 Widerrufsrecht</h2>
    <p class="mb-2">
      Es gelten die gesetzlichen Regelungen zum Widerrufsrecht für Fernabsatzverträge.
      Die vollständige Widerrufsbelehrung finden Sie unter:
    </p>
    <p>
      <a href="{% url 'legal:widerrufsbelehrung' %}" class="text-blue-600 hover:underline font-medium">
        Widerrufsbelehrung
      </a>
    </p>
  </section>

  {# ── §6 Laufzeit und Kündigung ─────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 6 Laufzeit und Kündigung</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Monatliche Abonnements verlängern sich automatisch um jeweils einen Monat,
        sofern nicht bis zum Ende der Laufzeit gekündigt wird.
      </li>
      <li>
        Jährliche Abonnements verlängern sich automatisch um ein weiteres Jahr,
        sofern nicht spätestens 14 Tage vor Ablauf gekündigt wird.
      </li>
      <li>
        Die Kündigung kann jederzeit über das Kundenkonto unter
        „Mein Bereich → Abonnement" erfolgen.
      </li>
      <li>
        Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt.
      </li>
    </ol>
  </section>

  {# ── §7 Haftung ────────────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 7 Haftungsbeschränkung</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Der Anbieter haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit.
      </li>
      <li>
        Bei leichter Fahrlässigkeit haftet der Anbieter nur bei Verletzung wesentlicher
        Vertragspflichten (Kardinalpflichten), begrenzt auf den vorhersehbaren,
        vertragstypischen Schaden.
      </li>
      <li>
        Die Haftung für Datenverlust wird auf den typischen Wiederherstellungsaufwand
        begrenzt, der bei regelmäßiger Datensicherung anfallen würde.
      </li>
      <li>
        Die vorstehenden Haftungsbeschränkungen gelten nicht für Schäden aus der Verletzung
        des Lebens, des Körpers oder der Gesundheit sowie für Ansprüche nach dem
        Produkthaftungsgesetz.
      </li>
    </ol>
  </section>

  {# ── §8 Datenschutz ────────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 8 Datenschutz</h2>
    <p>
      Informationen zur Verarbeitung personenbezogener Daten finden Sie in unserer
      <a href="{% url 'legal:datenschutz' %}" class="text-blue-600 hover:underline">Datenschutzerklärung</a>.
    </p>
  </section>

  {# ── §9 Schlussbestimmungen ─────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">§ 9 Schlussbestimmungen</h2>
    <ol class="list-decimal list-inside space-y-2">
      <li>
        Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des
        UN-Kaufrechts (CISG).
      </li>
      <li>
        Sollte eine Bestimmung dieser AGB unwirksam sein, bleibt die Wirksamkeit
        der übrigen Bestimmungen davon unberührt.
      </li>
      <li>
        Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS)
        bereit:
        <a href="https://ec.europa.eu/consumers/odr" target="_blank" rel="noopener noreferrer"
           class="text-blue-600 hover:underline">
          https://ec.europa.eu/consumers/odr
        </a>
      </li>
    </ol>
  </section>

</div>
{% endblock %}
```

---

## 4. Cookie Banner (3-Layer HTMX Implementation)

### Layer 1: Initial Banner

```html
{# templates/legal/includes/cookie_banner.html #}

<div id="cookie-banner"
     class="fixed bottom-0 inset-x-0 z-50 bg-white border-t border-gray-200 shadow-2xl p-6
            {% if cookie_consent_given %}hidden{% endif %}"
     role="dialog"
     aria-label="Cookie-Einstellungen"
     aria-modal="true">

  <div class="max-w-4xl mx-auto">
    <div id="cookie-banner-content">

      <h2 class="text-lg font-semibold mb-2">Wir verwenden Cookies</h2>
      <p class="text-sm text-gray-600 mb-4">
        Wir nutzen Cookies, um unsere Website bereitzustellen und zu verbessern.
        Einige Cookies sind technisch notwendig, andere helfen uns, die Website zu
        verbessern (Statistik) oder personalisierte Inhalte anzuzeigen (Marketing).
        Weitere Informationen finden Sie in unserer
        <a href="{% url 'legal:datenschutz' %}#cookies" class="text-blue-600 hover:underline">Datenschutzerklärung</a>.
      </p>

      {# THREE EQUAL BUTTONS — TTDSG §25 requirement #}
      <div class="flex flex-col sm:flex-row gap-3">

        {# Accept All #}
        <button type="button"
                hx-post="{% url 'legal:cookie_consent_save' %}"
                hx-vals='{"necessary": true, "statistics": true, "marketing": true, "external_media": true}'
                hx-target="#cookie-banner"
                hx-swap="outerHTML"
                class="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg
                       hover:bg-blue-700 transition text-center">
          Alle akzeptieren
        </button>

        {# Settings — opens Layer 2 #}
        <button type="button"
                hx-get="{% url 'legal:cookie_settings' %}"
                hx-target="#cookie-banner-content"
                hx-swap="innerHTML"
                class="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-medium rounded-lg
                       hover:bg-gray-300 transition text-center">
          Einstellungen
        </button>

        {# Necessary Only #}
        <button type="button"
                hx-post="{% url 'legal:cookie_consent_save' %}"
                hx-vals='{"necessary": true, "statistics": false, "marketing": false, "external_media": false}'
                hx-target="#cookie-banner"
                hx-swap="outerHTML"
                class="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-medium rounded-lg
                       hover:bg-gray-300 transition text-center">
          Nur notwendige
        </button>

      </div>
    </div>
  </div>
</div>
```

### Layer 2: Cookie Settings Panel

```html
{# templates/legal/includes/cookie_settings.html #}

<h2 class="text-lg font-semibold mb-4">Cookie-Einstellungen</h2>

<form hx-post="{% url 'legal:cookie_consent_save' %}"
      hx-target="#cookie-banner"
      hx-swap="outerHTML">
  {% csrf_token %}

  <div class="space-y-4 mb-6">

    {# Necessary — always on, cannot be toggled #}
    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div>
        <h3 class="font-medium">Notwendige Cookies</h3>
        <p class="text-xs text-gray-500">Technisch erforderlich fuer die Grundfunktionen der Website</p>
      </div>
      <div class="relative">
        <input type="checkbox" name="necessary" checked disabled
               class="sr-only peer" id="cookie-necessary">
        <label for="cookie-necessary"
               class="block w-11 h-6 bg-blue-600 rounded-full cursor-not-allowed
                      after:content-[''] after:absolute after:top-[2px] after:left-[22px]
                      after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all">
        </label>
        <input type="hidden" name="necessary" value="true">
        <span class="text-xs text-gray-400 mt-1 block text-right">Immer aktiv</span>
      </div>
    </div>

    {# Statistics — default OFF #}
    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
         x-data="{ enabled: false }">
      <div>
        <h3 class="font-medium">Statistik</h3>
        <p class="text-xs text-gray-500">Helfen uns zu verstehen, wie Besucher die Website nutzen (Matomo)</p>
      </div>
      <label class="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" name="statistics" x-model="enabled"
               class="sr-only peer" id="cookie-statistics">
        <div class="w-11 h-6 bg-gray-300 rounded-full peer
                    peer-checked:bg-blue-600 after:content-[''] after:absolute
                    after:top-[2px] after:left-[2px] after:bg-white after:rounded-full
                    after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full">
        </div>
      </label>
    </div>

    {# Marketing — default OFF #}
    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
         x-data="{ enabled: false }">
      <div>
        <h3 class="font-medium">Marketing</h3>
        <p class="text-xs text-gray-500">Ermöglichen personalisierte Werbung</p>
      </div>
      <label class="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" name="marketing" x-model="enabled"
               class="sr-only peer" id="cookie-marketing">
        <div class="w-11 h-6 bg-gray-300 rounded-full peer
                    peer-checked:bg-blue-600 after:content-[''] after:absolute
                    after:top-[2px] after:left-[2px] after:bg-white after:rounded-full
                    after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full">
        </div>
      </label>
    </div>

    {# External Media — default OFF #}
    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
         x-data="{ enabled: false }">
      <div>
        <h3 class="font-medium">Externe Medien</h3>
        <p class="text-xs text-gray-500">YouTube-Videos, Google Maps und andere externe Inhalte</p>
      </div>
      <label class="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" name="external_media" x-model="enabled"
               class="sr-only peer" id="cookie-external">
        <div class="w-11 h-6 bg-gray-300 rounded-full peer
                    peer-checked:bg-blue-600 after:content-[''] after:absolute
                    after:top-[2px] after:left-[2px] after:bg-white after:rounded-full
                    after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full">
        </div>
      </label>
    </div>

  </div>

  {# Action buttons #}
  <div class="flex flex-col sm:flex-row gap-3">
    <button type="submit"
            class="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg
                   hover:bg-blue-700 transition text-center">
      Auswahl speichern
    </button>
    <button type="button"
            hx-get="{% url 'legal:cookie_details' %}"
            hx-target="#cookie-banner-content"
            hx-swap="innerHTML"
            class="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-medium rounded-lg
                   hover:bg-gray-300 transition text-center text-sm">
      Cookie-Details anzeigen
    </button>
  </div>

</form>
```

### Layer 3: Detailed Cookie Table

```html
{# templates/legal/includes/cookie_details.html #}

<h2 class="text-lg font-semibold mb-4">Cookie-Details</h2>

<div class="overflow-x-auto mb-6">
  <table class="w-full text-xs border border-gray-200">
    <thead class="bg-gray-100">
      <tr>
        <th class="p-2 text-left border-b">Name</th>
        <th class="p-2 text-left border-b">Anbieter</th>
        <th class="p-2 text-left border-b">Kategorie</th>
        <th class="p-2 text-left border-b">Zweck</th>
        <th class="p-2 text-left border-b">Ablauf</th>
        <th class="p-2 text-left border-b">Typ</th>
      </tr>
    </thead>
    <tbody>
      <tr class="border-b bg-green-50">
        <td class="p-2"><code>sessionid</code></td>
        <td class="p-2">Lebenslauf-Builder</td>
        <td class="p-2">Notwendig</td>
        <td class="p-2">Sitzungsverwaltung fuer eingeloggte Nutzer</td>
        <td class="p-2">24 Stunden</td>
        <td class="p-2">HTTP</td>
      </tr>
      <tr class="border-b bg-green-50">
        <td class="p-2"><code>csrftoken</code></td>
        <td class="p-2">Lebenslauf-Builder</td>
        <td class="p-2">Notwendig</td>
        <td class="p-2">Schutz vor Cross-Site Request Forgery</td>
        <td class="p-2">1 Jahr</td>
        <td class="p-2">HTTP</td>
      </tr>
      <tr class="border-b bg-green-50">
        <td class="p-2"><code>cookie_consent</code></td>
        <td class="p-2">Lebenslauf-Builder</td>
        <td class="p-2">Notwendig</td>
        <td class="p-2">Speichert Ihre Cookie-Einstellungen</td>
        <td class="p-2">1 Jahr</td>
        <td class="p-2">HTTP</td>
      </tr>
      <tr class="border-b bg-yellow-50">
        <td class="p-2"><code>_pk_id</code></td>
        <td class="p-2">Matomo (self-hosted)</td>
        <td class="p-2">Statistik</td>
        <td class="p-2">Nutzer-Identifikation fuer anonyme Nutzungsstatistiken</td>
        <td class="p-2">13 Monate</td>
        <td class="p-2">HTTP</td>
      </tr>
      <tr class="border-b bg-yellow-50">
        <td class="p-2"><code>_pk_ses</code></td>
        <td class="p-2">Matomo (self-hosted)</td>
        <td class="p-2">Statistik</td>
        <td class="p-2">Kurzfristige Sitzungsdaten fuer Statistiken</td>
        <td class="p-2">30 Minuten</td>
        <td class="p-2">HTTP</td>
      </tr>
    </tbody>
  </table>
</div>

{# Back to settings button #}
<div class="flex gap-3">
  <button type="button"
          hx-get="{% url 'legal:cookie_settings' %}"
          hx-target="#cookie-banner-content"
          hx-swap="innerHTML"
          class="px-6 py-3 bg-gray-200 text-gray-800 font-medium rounded-lg
                 hover:bg-gray-300 transition">
    Zurück zu Einstellungen
  </button>
</div>
```

### Cookie Banner Dismissed Response

```html
{# templates/legal/includes/cookie_banner_dismissed.html #}
{# Returned after consent is saved — replaces the banner with nothing #}

<div id="cookie-banner" class="hidden"></div>
```

---

## 5. Widerrufsbelehrung (14-Day Withdrawal)

```html
{# templates/legal/widerrufsbelehrung.html #}

{% extends "base.html" %}
{% load i18n static %}

{% block title %}Widerrufsbelehrung | Lebenslauf-Builder{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto px-4 py-12">

  <h1 class="text-3xl font-bold mb-8">Widerrufsbelehrung</h1>

  {# ── Widerrufsrecht ────────────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Widerrufsrecht</h2>
    <p class="mb-4">
      Sie haben das Recht, binnen <strong>vierzehn Tagen</strong> ohne Angabe von Gründen
      diesen Vertrag zu widerrufen. Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag
      des Vertragsabschlusses.
    </p>
    <p class="mb-4">
      Um Ihr Widerrufsrecht auszuüben, müssen Sie uns
    </p>
    <address class="not-italic leading-relaxed mb-4 pl-4 border-l-4 border-blue-200">
      Lebenslauf-Builder GmbH<br>
      Musterstraße 123<br>
      10115 Berlin<br>
      E-Mail: widerruf@lebenslauf-builder.de<br>
      Telefon: +49 (0) 30 123 456 789
    </address>
    <p class="mb-4">
      mittels einer eindeutigen Erklärung (z.B. ein mit der Post versandter Brief oder
      E-Mail) über Ihren Entschluss, diesen Vertrag zu widerrufen, informieren.
      Sie können dafür das beigefügte Muster-Widerrufsformular verwenden, das jedoch
      nicht vorgeschrieben ist.
    </p>
    <p>
      Zur Wahrung der Widerrufsfrist reicht es aus, dass Sie die Mitteilung über die
      Ausübung des Widerrufsrechts vor Ablauf der Widerrufsfrist absenden.
    </p>
  </section>

  {# ── Folgen des Widerrufs ──────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Folgen des Widerrufs</h2>
    <p class="mb-4">
      Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von
      Ihnen erhalten haben, unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag
      zurückzuzahlen, an dem die Mitteilung über Ihren Widerruf dieses Vertrags bei uns
      eingegangen ist. Für diese Rückzahlung verwenden wir dasselbe Zahlungsmittel, das
      Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen
      wurde ausdrücklich etwas anderes vereinbart; in keinem Fall werden Ihnen wegen dieser
      Rückzahlung Entgelte berechnet.
    </p>
    <p class="mb-4">
      Haben Sie verlangt, dass die Dienstleistung während der Widerrufsfrist beginnen soll,
      so haben Sie uns einen angemessenen Betrag zu zahlen, der dem Anteil der bis zu dem
      Zeitpunkt, zu dem Sie uns von der Ausübung des Widerrufsrechts hinsichtlich dieses
      Vertrages unterrichten, bereits erbrachten Dienstleistungen im Vergleich zum
      Gesamtumfang der im Vertrag vorgesehenen Dienstleistungen entspricht.
    </p>
  </section>

  {# ── Vorzeitiges Erlöschen ─────────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Hinweis zum vorzeitigen Erlöschen des Widerrufsrechts</h2>
    <p class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      Das Widerrufsrecht erlischt vorzeitig, wenn wir die Dienstleistung vollständig
      erbracht haben und mit der Ausführung der Dienstleistung erst begonnen haben,
      nachdem Sie dazu Ihre ausdrückliche Zustimmung gegeben und gleichzeitig Ihre
      Kenntnis davon bestätigt haben, dass Sie Ihr Widerrufsrecht bei vollständiger
      Vertragserfüllung verlieren (§ 356 Abs. 4 BGB).
    </p>
  </section>

  {# ── Muster-Widerrufsformular ──────────────────── #}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Muster-Widerrufsformular</h2>
    <p class="mb-4 text-sm text-gray-500">
      (Wenn Sie den Vertrag widerrufen wollen, dann füllen Sie bitte dieses Formular aus und senden Sie es zurück.)
    </p>
    <div class="p-6 border border-gray-200 rounded-lg bg-gray-50">
      <p class="mb-2">An:</p>
      <p class="mb-4 pl-4">
        Lebenslauf-Builder GmbH<br>
        Musterstraße 123<br>
        10115 Berlin<br>
        E-Mail: widerruf@lebenslauf-builder.de
      </p>
      <p class="mb-2">
        Hiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über
        die Erbringung der folgenden Dienstleistung:
      </p>
      <p class="mb-2">_________________________________________________________</p>
      <p class="mb-2">Bestellt am (*) / erhalten am (*):</p>
      <p class="mb-2">_________________________________________________________</p>
      <p class="mb-2">Name des/der Verbraucher(s):</p>
      <p class="mb-2">_________________________________________________________</p>
      <p class="mb-2">Anschrift des/der Verbraucher(s):</p>
      <p class="mb-2">_________________________________________________________</p>
      <p class="mb-4">Datum, Unterschrift (nur bei Mitteilung auf Papier)</p>
      <p class="text-xs text-gray-400">(*) Unzutreffendes streichen.</p>
    </div>

    <div class="mt-4">
      <a href="{% static 'legal/widerrufsformular.pdf' %}"
         download="Widerrufsformular-Lebenslauf-Builder.pdf"
         class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Widerrufsformular herunterladen (PDF)
      </a>
    </div>
  </section>

  {# ── Online Widerruf (convenience) ─────────────── #}
  {% if user.is_authenticated and user.subscription.can_widerruf %}
  <section class="mb-8">
    <h2 class="text-xl font-semibold mb-3">Online-Widerruf</h2>
    <p class="mb-4">
      Sie können Ihren Widerruf auch direkt über Ihr Kundenkonto einreichen:
    </p>
    <a href="{% url 'payments:widerruf' %}"
       class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
      Widerruf online einreichen
    </a>
    <p class="text-sm text-gray-500 mt-2">
      Verbleibende Frist: {{ user.subscription.days_until_widerruf_expires }} Tage
    </p>
  </section>
  {% endif %}

</div>
{% endblock %}
```

---

## Footer Include (All Legal Links)

```html
{# templates/includes/footer.html #}

<footer class="bg-gray-900 text-gray-300 py-12 mt-auto">
  <div class="max-w-6xl mx-auto px-4">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">

      {# ... other footer columns ... #}

      {# Legal links — accessible from EVERY page #}
      <div>
        <h3 class="text-white font-semibold mb-4">Rechtliches</h3>
        <ul class="space-y-2 text-sm">
          <li><a href="{% url 'legal:impressum' %}" class="hover:text-white transition">Impressum</a></li>
          <li><a href="{% url 'legal:datenschutz' %}" class="hover:text-white transition">Datenschutzerklärung</a></li>
          <li><a href="{% url 'legal:agb' %}" class="hover:text-white transition">AGB</a></li>
          <li><a href="{% url 'legal:widerrufsbelehrung' %}" class="hover:text-white transition">Widerrufsbelehrung</a></li>
          <li>
            <a href="#" onclick="document.getElementById('cookie-banner').classList.remove('hidden'); return false;"
               class="hover:text-white transition">
              Cookie-Einstellungen
            </a>
          </li>
        </ul>
      </div>

    </div>

    <div class="border-t border-gray-700 mt-8 pt-8 text-center text-xs text-gray-500">
      &copy; {% now "Y" %} Lebenslauf-Builder GmbH. Alle Rechte vorbehalten.
    </div>
  </div>
</footer>
```
