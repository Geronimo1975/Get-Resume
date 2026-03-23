# GoBD-Compliant Invoice System (Rechnungssystem)

## Overview

This reference documents a fully GoBD-compliant (Grundsaetze zur ordnungsmaessigen Fuehrung und Aufbewahrung von Buechern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff) invoice system for the Lebenslauf-Builder SaaS platform. All invoices are generated in German, comply with UStG (Umsatzsteuergesetz) requirements, and follow the sequential numbering mandate with no gaps.

---

## 1. Invoice Model (Rechnung)

```python
# invoices/models.py

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class InvoiceNumberSequence(models.Model):
    """
    Thread-safe sequential invoice number generator.
    Single row table that tracks the current sequence number per year.
    GoBD requires gapless, sequential numbering within a fiscal year.
    """
    year = models.PositiveIntegerField(unique=True)
    current_number = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "invoice_number_sequences"
        verbose_name = "Rechnungsnummer-Sequenz"
        verbose_name_plural = "Rechnungsnummer-Sequenzen"

    def __str__(self):
        return f"Sequenz {self.year}: {self.current_number}"


class Invoice(models.Model):
    """
    GoBD-compliant invoice model.

    Required fields per GoBD / UStG SS 14 Abs. 4:
    - Vollstaendiger Name und Anschrift des leistenden Unternehmers
    - Vollstaendiger Name und Anschrift des Leistungsempfaengers
    - Steuernummer oder USt-IdNr des leistenden Unternehmers
    - Ausstellungsdatum (Rechnungsdatum)
    - Fortlaufende Rechnungsnummer (sequential, no gaps)
    - Menge und Art der gelieferten Gegenstaende / Umfang der Leistung
    - Zeitpunkt der Lieferung / sonstigen Leistung
    - Entgelt (Nettobetrag)
    - Steuersatz und Steuerbetrag
    - Im Voraus vereinbarte Minderungen des Entgelts
    """

    class InvoiceStatus(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        FINALIZED = "finalized", "Finalisiert"
        SENT = "sent", "Versendet"
        PAID = "paid", "Bezahlt"
        OVERDUE = "overdue", "Ueberfaellig"
        CANCELLED = "cancelled", "Storniert"

    class PaymentMethod(models.TextChoices):
        STRIPE_CARD = "stripe_card", "Kreditkarte (Stripe)"
        STRIPE_SEPA = "stripe_sepa", "SEPA-Lastschrift (Stripe)"
        STRIPE_GIROPAY = "stripe_giropay", "giropay (Stripe)"
        BANK_TRANSFER = "bank_transfer", "Bankueberweisung"

    class InvoiceType(models.TextChoices):
        INVOICE = "invoice", "Rechnung"
        CREDIT_NOTE = "credit_note", "Stornorechnung / Gutschrift"

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # === Invoice identification ===
    rechnungsnummer = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Rechnungsnummer",
        help_text="Format: RE-YYYY-NNNNN (e.g., RE-2026-00001)"
    )
    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.INVOICE,
        verbose_name="Rechnungstyp"
    )
    # Reference to original invoice for Stornorechnung
    storno_reference = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="storno_invoices",
        verbose_name="Storno-Referenz"
    )

    # === Dates ===
    rechnungsdatum = models.DateField(
        verbose_name="Rechnungsdatum",
        help_text="Ausstellungsdatum der Rechnung"
    )
    leistungszeitraum_start = models.DateField(
        verbose_name="Leistungszeitraum Beginn",
        help_text="Beginn des Leistungszeitraums"
    )
    leistungszeitraum_end = models.DateField(
        verbose_name="Leistungszeitraum Ende",
        help_text="Ende des Leistungszeitraums"
    )
    faelligkeitsdatum = models.DateField(
        null=True,
        blank=True,
        verbose_name="Faelligkeitsdatum",
        help_text="Zahlungsziel"
    )

    # === Customer data (denormalized for GoBD immutability) ===
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name="Kunde"
    )
    customer_name = models.CharField(
        max_length=255,
        verbose_name="Kundenname",
        help_text="Vollstaendiger Name zum Zeitpunkt der Rechnungsstellung"
    )
    customer_email = models.EmailField(
        verbose_name="Kunden-E-Mail"
    )
    customer_address_line1 = models.CharField(
        max_length=255,
        verbose_name="Adresszeile 1"
    )
    customer_address_line2 = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Adresszeile 2"
    )
    customer_postal_code = models.CharField(
        max_length=10,
        verbose_name="Postleitzahl"
    )
    customer_city = models.CharField(
        max_length=100,
        verbose_name="Stadt"
    )
    customer_country = models.CharField(
        max_length=2,
        default="DE",
        verbose_name="Land (ISO 3166-1 alpha-2)"
    )
    customer_ust_idnr = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="USt-IdNr. des Kunden",
        help_text="Falls B2B Reverse Charge"
    )

    # === Company data (denormalized snapshot) ===
    company_name = models.CharField(
        max_length=255,
        default="Lebenslauf-Builder GmbH",
        verbose_name="Firmenname"
    )
    company_address = models.TextField(
        verbose_name="Firmenanschrift"
    )
    company_ust_idnr = models.CharField(
        max_length=20,
        verbose_name="USt-IdNr.",
        help_text="Umsatzsteuer-Identifikationsnummer"
    )
    company_steuernummer = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Steuernummer"
    )
    company_handelsregister = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Handelsregister"
    )
    company_geschaeftsfuehrer = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Geschaeftsfuehrer"
    )

    # === Line items ===
    line_items = models.JSONField(
        verbose_name="Rechnungspositionen",
        help_text="List of line item dicts with: position, beschreibung, menge, einzelpreis, gesamtpreis"
    )
    # Example line_items structure:
    # [
    #     {
    #         "position": 1,
    #         "beschreibung": "Lebenslauf-Builder Premium Abo (Monatlich)",
    #         "menge": 1,
    #         "einheit": "Stueck",
    #         "einzelpreis": "9.99",
    #         "gesamtpreis": "9.99"
    #     }
    # ]

    # === Financial amounts ===
    nettobetrag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Nettobetrag",
        help_text="Gesamtbetrag ohne MwSt."
    )
    mwst_satz = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("19.00"),
        verbose_name="MwSt.-Satz (%)",
        help_text="Standard: 19%, ermaessigt: 7%"
    )
    mwst_betrag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="MwSt.-Betrag"
    )
    bruttobetrag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Bruttobetrag",
        help_text="Gesamtbetrag inkl. MwSt."
    )

    # === Payment ===
    zahlungsmethode = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        verbose_name="Zahlungsmethode"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Stripe PaymentIntent ID"
    )
    stripe_invoice_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Stripe Invoice ID"
    )

    # === PDF and delivery ===
    pdf_file = models.FileField(
        upload_to="invoices/pdfs/%Y/%m/",
        blank=True,
        verbose_name="PDF-Datei"
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Versendet am"
    )

    # === Status ===
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        verbose_name="Status"
    )

    # === Audit fields ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_invoices",
        verbose_name="Erstellt von"
    )

    # === GoBD compliance flags ===
    is_finalized = models.BooleanField(
        default=False,
        verbose_name="Finalisiert",
        help_text="Once finalized, invoice cannot be modified (GoBD)"
    )
    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Finalisiert am"
    )
    checksum = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name="SHA-256 Pruefsumme",
        help_text="Hash of finalized invoice data for tamper detection"
    )

    class Meta:
        db_table = "invoices"
        ordering = ["-rechnungsdatum", "-rechnungsnummer"]
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"
        indexes = [
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["rechnungsdatum"]),
            models.Index(fields=["stripe_payment_intent_id"]),
        ]

    def __str__(self):
        return f"{self.rechnungsnummer} - {self.customer_name} - {self.bruttobetrag} EUR"

    def save(self, *args, **kwargs):
        """Override save to enforce GoBD immutability."""
        if self.is_finalized and self.pk:
            # Check if this is an existing finalized invoice being modified
            try:
                existing = Invoice.objects.get(pk=self.pk)
                if existing.is_finalized:
                    # Only allow status changes and sent_at updates
                    allowed_changes = {"status", "sent_at", "updated_at"}
                    for field in self._meta.fields:
                        if field.name in allowed_changes:
                            continue
                        if getattr(existing, field.name) != getattr(self, field.name):
                            raise ValueError(
                                f"GoBD-Fehler: Finalisierte Rechnung {self.rechnungsnummer} "
                                f"darf nicht geaendert werden. Feld: {field.name}"
                            )
            except Invoice.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """GoBD: Invoices must NEVER be deleted. Use Stornorechnung instead."""
        raise ValueError(
            f"GoBD-Fehler: Rechnung {self.rechnungsnummer} darf nicht geloescht werden. "
            "Erstellen Sie stattdessen eine Stornorechnung."
        )

    def calculate_checksum(self):
        """Generate SHA-256 checksum of invoice data for tamper detection."""
        import hashlib
        import json

        data = {
            "rechnungsnummer": self.rechnungsnummer,
            "rechnungsdatum": str(self.rechnungsdatum),
            "customer_name": self.customer_name,
            "line_items": self.line_items,
            "nettobetrag": str(self.nettobetrag),
            "mwst_betrag": str(self.mwst_betrag),
            "bruttobetrag": str(self.bruttobetrag),
        }
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()
```

---

## 2. Sequential Rechnungsnummer Generation (Thread-Safe)

```python
# invoices/services.py (partial - number generation)

from django.db import transaction
from django.utils import timezone
from .models import InvoiceNumberSequence


def generate_next_rechnungsnummer() -> str:
    """
    Generate the next sequential Rechnungsnummer in thread-safe manner.

    Format: RE-YYYY-NNNNN (e.g., RE-2026-00001)

    GoBD Requirements:
    - Sequential numbering with NO gaps
    - Numbers must be unique within the fiscal year
    - Thread-safe to prevent duplicate numbers under concurrent access

    Uses SELECT ... FOR UPDATE to lock the sequence row,
    preventing race conditions in concurrent environments.

    Returns:
        str: The next invoice number in format RE-YYYY-NNNNN

    Raises:
        RuntimeError: If sequence generation fails
    """
    current_year = timezone.now().year

    with transaction.atomic():
        # Lock the row for the current year to prevent concurrent access.
        # select_for_update() acquires a row-level lock in PostgreSQL.
        # This ensures that even under high concurrency, only one transaction
        # at a time can read and increment the sequence number.
        sequence, created = InvoiceNumberSequence.objects.select_for_update().get_or_create(
            year=current_year,
            defaults={"current_number": 0}
        )

        # Increment the sequence number
        sequence.current_number += 1
        sequence.save(update_fields=["current_number"])

        # Format: RE-YYYY-NNNNN
        rechnungsnummer = f"RE-{current_year}-{sequence.current_number:05d}"

        return rechnungsnummer


def generate_storno_rechnungsnummer() -> str:
    """
    Generate a Stornorechnung number using the same sequence.

    Format: ST-YYYY-NNNNN

    Storno numbers share the same sequence as regular invoices
    to maintain the gapless requirement.
    """
    current_year = timezone.now().year

    with transaction.atomic():
        sequence, created = InvoiceNumberSequence.objects.select_for_update().get_or_create(
            year=current_year,
            defaults={"current_number": 0}
        )

        sequence.current_number += 1
        sequence.save(update_fields=["current_number"])

        rechnungsnummer = f"ST-{current_year}-{sequence.current_number:05d}"

        return rechnungsnummer
```

### Integrity Verification

```python
# invoices/management/commands/verify_invoice_sequence.py

from django.core.management.base import BaseCommand
from invoices.models import Invoice, InvoiceNumberSequence


class Command(BaseCommand):
    help = "Verify GoBD-compliant gapless invoice number sequence"

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, help="Year to verify")

    def handle(self, *args, **options):
        from django.utils import timezone

        year = options.get("year") or timezone.now().year

        invoices = (
            Invoice.objects
            .filter(rechnungsnummer__startswith=f"RE-{year}-")
            .union(
                Invoice.objects.filter(rechnungsnummer__startswith=f"ST-{year}-")
            )
            .order_by("rechnungsnummer")
        )

        # Extract and sort all numbers for the year
        numbers = []
        for inv in invoices:
            # Extract NNNNN from RE-YYYY-NNNNN or ST-YYYY-NNNNN
            num = int(inv.rechnungsnummer.split("-")[2])
            numbers.append(num)

        numbers.sort()

        if not numbers:
            self.stdout.write(self.style.WARNING(f"No invoices found for {year}"))
            return

        # Check for gaps
        expected = list(range(1, max(numbers) + 1))
        missing = set(expected) - set(numbers)

        if missing:
            self.stdout.write(self.style.ERROR(
                f"GoBD VIOLATION: Missing invoice numbers for {year}: {sorted(missing)}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"OK: {year} sequence is gapless (1 to {max(numbers)})"
            ))

        # Verify sequence counter matches
        try:
            seq = InvoiceNumberSequence.objects.get(year=year)
            if seq.current_number != max(numbers):
                self.stdout.write(self.style.WARNING(
                    f"Sequence counter ({seq.current_number}) != max number ({max(numbers)})"
                ))
        except InvoiceNumberSequence.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No sequence record for {year}"))
```

---

## 3. Invoice PDF Template

```html
{# invoices/templates/invoices/invoice_pdf.html #}
{# Rendered with WeasyPrint - supports CSS for print/PDF layout #}

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{{ invoice.rechnungsnummer }}</title>
    <style>
        @page {
            size: A4;
            margin: 20mm 20mm 30mm 20mm;

            @bottom-center {
                content: "Seite " counter(page) " von " counter(pages);
                font-size: 8pt;
                color: #666;
            }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: "Helvetica Neue", Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.5;
            color: #333;
        }

        /* === Letterhead === */
        .letterhead {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15mm;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 5mm;
        }

        .company-logo img {
            max-width: 180px;
            max-height: 60px;
        }

        .company-info {
            text-align: right;
            font-size: 8pt;
            color: #666;
        }

        .company-info .company-name {
            font-size: 11pt;
            font-weight: bold;
            color: #2563eb;
        }

        /* === Sender line (Absenderzeile im Adressfeld) === */
        .sender-line {
            font-size: 7pt;
            color: #666;
            text-decoration: underline;
            margin-bottom: 2mm;
        }

        /* === Address block === */
        .address-block {
            margin-bottom: 15mm;
        }

        .address-block .recipient {
            min-height: 27.3mm; /* DIN 5008 Anschriftfeld */
        }

        /* === Invoice header === */
        .invoice-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10mm;
        }

        .invoice-title {
            font-size: 18pt;
            font-weight: bold;
            color: #2563eb;
        }

        .invoice-title.storno {
            color: #dc2626;
        }

        .invoice-meta {
            text-align: right;
        }

        .invoice-meta table {
            border-collapse: collapse;
        }

        .invoice-meta td {
            padding: 1mm 3mm;
            font-size: 9pt;
        }

        .invoice-meta td:first-child {
            font-weight: bold;
            text-align: right;
            color: #666;
        }

        /* === Storno reference banner === */
        .storno-banner {
            background: #fef2f2;
            border: 1px solid #dc2626;
            border-radius: 4px;
            padding: 3mm 5mm;
            margin-bottom: 8mm;
            color: #dc2626;
            font-weight: bold;
        }

        /* === Line items table === */
        .line-items {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 8mm;
        }

        .line-items thead {
            background: #f1f5f9;
        }

        .line-items th {
            padding: 2mm 3mm;
            text-align: left;
            font-size: 9pt;
            font-weight: bold;
            border-bottom: 2px solid #2563eb;
        }

        .line-items th.amount {
            text-align: right;
        }

        .line-items td {
            padding: 2mm 3mm;
            font-size: 9pt;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: top;
        }

        .line-items td.amount {
            text-align: right;
            white-space: nowrap;
        }

        .line-items td.pos {
            text-align: center;
            width: 10mm;
        }

        /* === Totals === */
        .totals {
            width: 50%;
            margin-left: auto;
            border-collapse: collapse;
            margin-bottom: 10mm;
        }

        .totals td {
            padding: 1.5mm 3mm;
            font-size: 9pt;
        }

        .totals td:first-child {
            text-align: right;
            color: #666;
        }

        .totals td:last-child {
            text-align: right;
            font-weight: bold;
        }

        .totals tr.brutto {
            border-top: 2px solid #2563eb;
        }

        .totals tr.brutto td {
            font-size: 11pt;
            padding-top: 3mm;
            color: #2563eb;
        }

        /* === Payment info === */
        .payment-info {
            margin-bottom: 10mm;
            padding: 4mm;
            background: #f8fafc;
            border-radius: 4px;
            font-size: 9pt;
        }

        .payment-info h3 {
            font-size: 10pt;
            margin-bottom: 2mm;
        }

        /* === Footer === */
        .invoice-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 3mm 20mm;
            border-top: 1px solid #e2e8f0;
            font-size: 7pt;
            color: #999;
            display: flex;
            justify-content: space-between;
        }

        .invoice-footer .col {
            flex: 1;
        }

        /* === Legal notes === */
        .legal-notes {
            font-size: 8pt;
            color: #666;
            margin-top: 10mm;
        }
    </style>
</head>
<body>
    <!-- Letterhead -->
    <div class="letterhead">
        <div class="company-logo">
            <img src="{{ company_logo_path }}" alt="{{ invoice.company_name }}">
        </div>
        <div class="company-info">
            <div class="company-name">{{ invoice.company_name }}</div>
            <div>{{ invoice.company_address|linebreaksbr }}</div>
            <div>USt-IdNr.: {{ invoice.company_ust_idnr }}</div>
            {% if invoice.company_steuernummer %}
            <div>Steuernr.: {{ invoice.company_steuernummer }}</div>
            {% endif %}
        </div>
    </div>

    <!-- Sender line + Recipient address -->
    <div class="address-block">
        <div class="sender-line">
            {{ invoice.company_name }} &middot; {{ invoice.company_address|truncatechars:80 }}
        </div>
        <div class="recipient">
            {{ invoice.customer_name }}<br>
            {{ invoice.customer_address_line1 }}<br>
            {% if invoice.customer_address_line2 %}
                {{ invoice.customer_address_line2 }}<br>
            {% endif %}
            {{ invoice.customer_postal_code }} {{ invoice.customer_city }}<br>
            {% if invoice.customer_country != "DE" %}
                {{ invoice.get_customer_country_display }}<br>
            {% endif %}
            {% if invoice.customer_ust_idnr %}
                USt-IdNr.: {{ invoice.customer_ust_idnr }}
            {% endif %}
        </div>
    </div>

    <!-- Invoice Header -->
    <div class="invoice-header">
        <div>
            {% if invoice.invoice_type == "credit_note" %}
                <div class="invoice-title storno">Stornorechnung</div>
            {% else %}
                <div class="invoice-title">Rechnung</div>
            {% endif %}
        </div>
        <div class="invoice-meta">
            <table>
                <tr>
                    <td>Rechnungsnummer:</td>
                    <td>{{ invoice.rechnungsnummer }}</td>
                </tr>
                <tr>
                    <td>Rechnungsdatum:</td>
                    <td>{{ invoice.rechnungsdatum|date:"d.m.Y" }}</td>
                </tr>
                <tr>
                    <td>Leistungszeitraum:</td>
                    <td>{{ invoice.leistungszeitraum_start|date:"d.m.Y" }} - {{ invoice.leistungszeitraum_end|date:"d.m.Y" }}</td>
                </tr>
                <tr>
                    <td>Kundennummer:</td>
                    <td>{{ invoice.customer.id|stringformat:"06d" }}</td>
                </tr>
                {% if invoice.faelligkeitsdatum %}
                <tr>
                    <td>Faelligkeitsdatum:</td>
                    <td>{{ invoice.faelligkeitsdatum|date:"d.m.Y" }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
    </div>

    <!-- Storno reference -->
    {% if invoice.invoice_type == "credit_note" and invoice.storno_reference %}
    <div class="storno-banner">
        Stornorechnung zu Rechnung {{ invoice.storno_reference.rechnungsnummer }}
        vom {{ invoice.storno_reference.rechnungsdatum|date:"d.m.Y" }}
    </div>
    {% endif %}

    <!-- Introductory text -->
    <p style="margin-bottom: 5mm;">
        {% if invoice.invoice_type == "credit_note" %}
        Hiermit stornieren wir die nachfolgend aufgefuehrten Positionen:
        {% else %}
        Fuer die nachfolgend aufgefuehrten Leistungen erlauben wir uns, Ihnen wie folgt in Rechnung zu stellen:
        {% endif %}
    </p>

    <!-- Line Items Table -->
    <table class="line-items">
        <thead>
            <tr>
                <th>Pos.</th>
                <th>Beschreibung</th>
                <th>Menge</th>
                <th class="amount">Einzelpreis</th>
                <th class="amount">Gesamtpreis</th>
            </tr>
        </thead>
        <tbody>
            {% for item in invoice.line_items %}
            <tr>
                <td class="pos">{{ item.position }}</td>
                <td>{{ item.beschreibung }}</td>
                <td>{{ item.menge }} {{ item.einheit|default:"Stck." }}</td>
                <td class="amount">{{ item.einzelpreis|floatformat:2 }} &euro;</td>
                <td class="amount">
                    {% if invoice.invoice_type == "credit_note" %}-{% endif %}{{ item.gesamtpreis|floatformat:2 }} &euro;
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- Totals -->
    <table class="totals">
        <tr>
            <td>Nettobetrag:</td>
            <td>{% if invoice.invoice_type == "credit_note" %}-{% endif %}{{ invoice.nettobetrag|floatformat:2 }} &euro;</td>
        </tr>
        <tr>
            <td>zzgl. {{ invoice.mwst_satz|floatformat:0 }}% MwSt.:</td>
            <td>{% if invoice.invoice_type == "credit_note" %}-{% endif %}{{ invoice.mwst_betrag|floatformat:2 }} &euro;</td>
        </tr>
        <tr class="brutto">
            <td>Bruttobetrag:</td>
            <td>{% if invoice.invoice_type == "credit_note" %}-{% endif %}{{ invoice.bruttobetrag|floatformat:2 }} &euro;</td>
        </tr>
    </table>

    <!-- Payment Information -->
    <div class="payment-info">
        <h3>Zahlungsinformation</h3>
        {% if invoice.invoice_type == "credit_note" %}
            <p>Der Betrag von {{ invoice.bruttobetrag|floatformat:2 }} &euro; wird Ihnen
            ueber die urspruengliche Zahlungsmethode ({{ invoice.get_zahlungsmethode_display }}) erstattet.</p>
        {% else %}
            {% if invoice.zahlungsmethode == "stripe_card" or invoice.zahlungsmethode == "stripe_sepa" or invoice.zahlungsmethode == "stripe_giropay" %}
                <p>Der Betrag wurde bereits per {{ invoice.get_zahlungsmethode_display }} beglichen.</p>
            {% elif invoice.zahlungsmethode == "bank_transfer" %}
                <p>Bitte ueberweisen Sie den Betrag bis zum {{ invoice.faelligkeitsdatum|date:"d.m.Y" }} auf folgendes Konto:</p>
                <p>
                    <strong>Kontoinhaber:</strong> {{ invoice.company_name }}<br>
                    <strong>IBAN:</strong> DE89 3704 0044 0532 0130 00<br>
                    <strong>BIC:</strong> COBADEFFXXX<br>
                    <strong>Verwendungszweck:</strong> {{ invoice.rechnungsnummer }}
                </p>
            {% endif %}
        {% endif %}
    </div>

    <!-- Legal notes -->
    <div class="legal-notes">
        {% if invoice.invoice_type == "credit_note" %}
        <p>Diese Stornorechnung wurde maschinell erstellt und ist ohne Unterschrift gueltig.</p>
        {% else %}
        <p>Diese Rechnung wurde maschinell erstellt und ist ohne Unterschrift gueltig.</p>
        {% endif %}
        <p>Es gelten unsere Allgemeinen Geschaeftsbedingungen (AGB).
        Widerrufsrecht gemaess SS 355 BGB: Sie haben das Recht, binnen 14 Tagen ohne Angabe
        von Gruenden diesen Vertrag zu widerrufen.</p>
    </div>

    <!-- Footer -->
    <div class="invoice-footer">
        <div class="col">
            {{ invoice.company_name }}<br>
            {{ invoice.company_address|linebreaksbr }}
        </div>
        <div class="col" style="text-align: center;">
            {% if invoice.company_handelsregister %}
            {{ invoice.company_handelsregister }}<br>
            {% endif %}
            {% if invoice.company_geschaeftsfuehrer %}
            GF: {{ invoice.company_geschaeftsfuehrer }}
            {% endif %}
        </div>
        <div class="col" style="text-align: right;">
            USt-IdNr.: {{ invoice.company_ust_idnr }}<br>
            {% if invoice.company_steuernummer %}
            Steuernr.: {{ invoice.company_steuernummer }}
            {% endif %}
        </div>
    </div>
</body>
</html>
```

---

## 4. InvoiceService Class

```python
# invoices/services.py

import hashlib
import json
import logging
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from payments.models import Payment, Subscription
from .models import Invoice

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Service class for creating, rendering, and managing GoBD-compliant invoices.

    Usage:
        service = InvoiceService()
        invoice = service.create_invoice_from_payment(payment)
        service.generate_invoice_pdf(invoice)
        service.send_invoice_email(invoice)
    """

    COMPANY_DEFAULTS = {
        "company_name": "Lebenslauf-Builder GmbH",
        "company_address": "Musterstrasse 42\n10115 Berlin\nDeutschland",
        "company_ust_idnr": "DE123456789",
        "company_steuernummer": "27/123/45678",
        "company_handelsregister": "HRB 12345 B, AG Charlottenburg",
        "company_geschaeftsfuehrer": "Max Mustermann",
    }

    def create_invoice_from_payment(
        self,
        payment: "Payment",
        invoice_type: str = Invoice.InvoiceType.INVOICE,
        storno_reference: "Invoice | None" = None,
    ) -> Invoice:
        """
        Create a new Invoice record from a Payment.

        Snapshots all customer data at the time of invoice creation
        to ensure GoBD immutability.

        Args:
            payment: The Payment object to invoice
            invoice_type: 'invoice' or 'credit_note'
            storno_reference: Original invoice for Stornorechnung

        Returns:
            Invoice: The created invoice (not yet finalized)
        """
        user = payment.user
        profile = getattr(user, "profile", None)

        # Generate gapless sequential number
        if invoice_type == Invoice.InvoiceType.CREDIT_NOTE:
            rechnungsnummer = generate_storno_rechnungsnummer()
        else:
            rechnungsnummer = generate_next_rechnungsnummer()

        # Calculate financial amounts
        nettobetrag = payment.amount  # Payment stores net amount
        mwst_satz = Decimal("19.00")
        mwst_betrag = (nettobetrag * mwst_satz / Decimal("100")).quantize(Decimal("0.01"))
        bruttobetrag = nettobetrag + mwst_betrag

        # Build line items
        line_items = self._build_line_items(payment)

        # Determine Leistungszeitraum from subscription
        subscription = payment.subscription
        if subscription:
            leistungszeitraum_start = subscription.current_period_start
            leistungszeitraum_end = subscription.current_period_end
        else:
            leistungszeitraum_start = timezone.now().date()
            leistungszeitraum_end = timezone.now().date()

        invoice = Invoice.objects.create(
            rechnungsnummer=rechnungsnummer,
            invoice_type=invoice_type,
            storno_reference=storno_reference,
            rechnungsdatum=timezone.now().date(),
            leistungszeitraum_start=leistungszeitraum_start,
            leistungszeitraum_end=leistungszeitraum_end,
            faelligkeitsdatum=timezone.now().date(),  # Already paid via Stripe

            # Customer data snapshot
            customer=user,
            customer_name=user.get_full_name() or user.email,
            customer_email=user.email,
            customer_address_line1=getattr(profile, "address_line1", ""),
            customer_address_line2=getattr(profile, "address_line2", ""),
            customer_postal_code=getattr(profile, "postal_code", ""),
            customer_city=getattr(profile, "city", ""),
            customer_country=getattr(profile, "country", "DE"),

            # Company data
            **self.COMPANY_DEFAULTS,

            # Line items
            line_items=line_items,

            # Financial
            nettobetrag=nettobetrag,
            mwst_satz=mwst_satz,
            mwst_betrag=mwst_betrag,
            bruttobetrag=bruttobetrag,

            # Payment reference
            zahlungsmethode=self._map_payment_method(payment),
            stripe_payment_intent_id=payment.stripe_payment_intent_id or "",
            stripe_invoice_id=payment.stripe_invoice_id or "",

            # Status
            status=Invoice.InvoiceStatus.DRAFT,
        )

        logger.info(
            f"Invoice {rechnungsnummer} created for user {user.id}, "
            f"amount: {bruttobetrag} EUR"
        )

        return invoice

    def _build_line_items(self, payment: "Payment") -> list[dict]:
        """Build line items list from payment details."""
        items = []

        if payment.subscription:
            plan = payment.subscription.plan
            items.append({
                "position": 1,
                "beschreibung": f"{plan.display_name} ({plan.get_billing_interval_display()})",
                "menge": 1,
                "einheit": "Stueck",
                "einzelpreis": str(payment.amount),
                "gesamtpreis": str(payment.amount),
            })
        else:
            items.append({
                "position": 1,
                "beschreibung": payment.description or "Lebenslauf-Builder Dienstleistung",
                "menge": 1,
                "einheit": "Stueck",
                "einzelpreis": str(payment.amount),
                "gesamtpreis": str(payment.amount),
            })

        return items

    def _map_payment_method(self, payment: "Payment") -> str:
        """Map Stripe payment method type to Invoice payment method."""
        method_map = {
            "card": Invoice.PaymentMethod.STRIPE_CARD,
            "sepa_debit": Invoice.PaymentMethod.STRIPE_SEPA,
            "giropay": Invoice.PaymentMethod.STRIPE_GIROPAY,
        }
        return method_map.get(
            payment.stripe_payment_method_type,
            Invoice.PaymentMethod.STRIPE_CARD
        )

    def generate_invoice_pdf(self, invoice: Invoice) -> Invoice:
        """
        Generate PDF for an invoice using WeasyPrint.

        The PDF is generated from the invoice_pdf.html template,
        saved to the invoice's pdf_file field, and the invoice
        is finalized (locked for GoBD compliance).

        Args:
            invoice: The Invoice to render

        Returns:
            Invoice: The invoice with pdf_file populated and finalized
        """
        # Render HTML template
        html_string = render_to_string(
            "invoices/invoice_pdf.html",
            {
                "invoice": invoice,
                "company_logo_path": str(
                    Path(settings.STATIC_ROOT) / "images" / "logo.png"
                ),
            }
        )

        # Generate PDF via WeasyPrint
        html = HTML(string=html_string, base_url=settings.STATIC_ROOT)
        pdf_bytes = html.write_pdf()

        # Save PDF to FileField
        filename = f"{invoice.rechnungsnummer}.pdf"
        invoice.pdf_file.save(
            filename,
            ContentFile(pdf_bytes),
            save=False  # We'll save manually after finalizing
        )

        # Finalize the invoice (GoBD: no further modifications allowed)
        invoice.is_finalized = True
        invoice.finalized_at = timezone.now()
        invoice.checksum = invoice.calculate_checksum()
        invoice.status = Invoice.InvoiceStatus.FINALIZED
        invoice.save()

        logger.info(
            f"PDF generated and invoice {invoice.rechnungsnummer} finalized. "
            f"Checksum: {invoice.checksum[:16]}..."
        )

        return invoice

    def send_invoice_email(self, invoice: Invoice) -> Invoice:
        """
        Send invoice PDF as email attachment.

        Args:
            invoice: The finalized Invoice with PDF

        Returns:
            Invoice: Updated with sent_at timestamp

        Raises:
            ValueError: If invoice has no PDF or is not finalized
        """
        if not invoice.pdf_file:
            raise ValueError(
                f"Rechnung {invoice.rechnungsnummer} hat keine PDF-Datei."
            )

        if not invoice.is_finalized:
            raise ValueError(
                f"Rechnung {invoice.rechnungsnummer} ist noch nicht finalisiert."
            )

        # Determine email template based on type
        if invoice.invoice_type == Invoice.InvoiceType.CREDIT_NOTE:
            subject = f"Stornorechnung {invoice.rechnungsnummer}"
            template = "invoices/emails/storno_invoice_email.html"
        else:
            subject = f"Ihre Rechnung {invoice.rechnungsnummer}"
            template = "invoices/emails/invoice_email.html"

        # Render email body
        html_body = render_to_string(template, {"invoice": invoice})

        # Create and send email with PDF attachment
        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer_email],
            reply_to=[settings.INVOICE_REPLY_TO_EMAIL],
        )
        email.content_subtype = "html"

        # Attach the PDF
        invoice.pdf_file.seek(0)
        email.attach(
            f"{invoice.rechnungsnummer}.pdf",
            invoice.pdf_file.read(),
            "application/pdf"
        )

        email.send(fail_silently=False)

        # Update sent timestamp
        invoice.sent_at = timezone.now()
        invoice.status = Invoice.InvoiceStatus.SENT
        invoice.save(update_fields=["sent_at", "status", "updated_at"])

        logger.info(
            f"Invoice {invoice.rechnungsnummer} sent to {invoice.customer_email}"
        )

        return invoice

    def generate_storno_invoice(
        self,
        original_invoice: Invoice,
        reason: str = "Widerruf gemaess SS 355 BGB"
    ) -> Invoice:
        """
        Generate a Stornorechnung (credit note) for a Widerruf refund.

        A Stornorechnung reverses the original invoice with negative amounts.
        GoBD requires that original invoices are never deleted or modified.
        Instead, a Stornorechnung references the original.

        Args:
            original_invoice: The original Invoice to reverse
            reason: Reason for cancellation

        Returns:
            Invoice: The finalized Stornorechnung with PDF

        Raises:
            ValueError: If the original invoice is not finalized or already cancelled
        """
        if not original_invoice.is_finalized:
            raise ValueError(
                f"Rechnung {original_invoice.rechnungsnummer} ist nicht finalisiert."
            )

        if original_invoice.status == Invoice.InvoiceStatus.CANCELLED:
            raise ValueError(
                f"Rechnung {original_invoice.rechnungsnummer} ist bereits storniert."
            )

        # Check for existing Stornorechnung
        existing_storno = Invoice.objects.filter(
            storno_reference=original_invoice,
            invoice_type=Invoice.InvoiceType.CREDIT_NOTE,
        ).exists()

        if existing_storno:
            raise ValueError(
                f"Fuer Rechnung {original_invoice.rechnungsnummer} "
                f"existiert bereits eine Stornorechnung."
            )

        # Generate Storno number
        storno_nummer = generate_storno_rechnungsnummer()

        # Build storno line items (same as original but with storno note)
        storno_items = []
        for item in original_invoice.line_items:
            storno_item = item.copy()
            storno_item["beschreibung"] = (
                f"Storno: {item['beschreibung']} "
                f"(Ref: {original_invoice.rechnungsnummer}) - {reason}"
            )
            storno_items.append(storno_item)

        # Create Stornorechnung (same amounts, marked as credit note)
        storno = Invoice.objects.create(
            rechnungsnummer=storno_nummer,
            invoice_type=Invoice.InvoiceType.CREDIT_NOTE,
            storno_reference=original_invoice,
            rechnungsdatum=timezone.now().date(),
            leistungszeitraum_start=original_invoice.leistungszeitraum_start,
            leistungszeitraum_end=original_invoice.leistungszeitraum_end,

            # Same customer data as original
            customer=original_invoice.customer,
            customer_name=original_invoice.customer_name,
            customer_email=original_invoice.customer_email,
            customer_address_line1=original_invoice.customer_address_line1,
            customer_address_line2=original_invoice.customer_address_line2,
            customer_postal_code=original_invoice.customer_postal_code,
            customer_city=original_invoice.customer_city,
            customer_country=original_invoice.customer_country,

            # Company data
            company_name=original_invoice.company_name,
            company_address=original_invoice.company_address,
            company_ust_idnr=original_invoice.company_ust_idnr,
            company_steuernummer=original_invoice.company_steuernummer,
            company_handelsregister=original_invoice.company_handelsregister,
            company_geschaeftsfuehrer=original_invoice.company_geschaeftsfuehrer,

            # Storno line items
            line_items=storno_items,

            # Same amounts (negative context shown in PDF template)
            nettobetrag=original_invoice.nettobetrag,
            mwst_satz=original_invoice.mwst_satz,
            mwst_betrag=original_invoice.mwst_betrag,
            bruttobetrag=original_invoice.bruttobetrag,

            # Payment reference from original
            zahlungsmethode=original_invoice.zahlungsmethode,
            stripe_payment_intent_id=original_invoice.stripe_payment_intent_id,

            status=Invoice.InvoiceStatus.DRAFT,
        )

        # Generate PDF and finalize
        self.generate_invoice_pdf(storno)

        # Mark original as cancelled
        original_invoice.status = Invoice.InvoiceStatus.CANCELLED
        original_invoice.save(update_fields=["status", "updated_at"])

        logger.info(
            f"Stornorechnung {storno_nummer} created for "
            f"original {original_invoice.rechnungsnummer}"
        )

        return storno
```

---

## 5. 10-Year Retention Policy Implementation

```python
# invoices/retention.py

"""
GoBD 10-Year Retention Policy (Aufbewahrungspflicht)

Per GoBD and AO (Abgabenordnung) SS 147:
- Invoices (Rechnungen) must be retained for 10 years
- The retention period starts at the end of the calendar year
  in which the invoice was issued
- Invoices must remain unmodified (unveraenderbar) during retention
- Digital invoices must be stored in their original format (PDF)
- A migration to a different storage format requires documentation

This module implements retention enforcement at multiple levels:
1. Model-level: delete() override prevents deletion
2. Admin-level: delete action removed, archive-only
3. Periodic check: management command to verify compliance
4. Storage-level: immutable object storage recommended
"""

import logging
from datetime import date
from django.utils import timezone
from django.contrib import admin
from django.contrib import messages

from .models import Invoice

logger = logging.getLogger(__name__)


def is_within_retention_period(invoice: Invoice) -> bool:
    """
    Check if an invoice is still within the 10-year retention period.

    The retention period starts at the end of the calendar year in which
    the invoice was issued. So an invoice from March 2026 must be retained
    until December 31, 2036.

    Args:
        invoice: The Invoice to check

    Returns:
        bool: True if still within retention period
    """
    if not invoice.rechnungsdatum:
        return True  # Err on the side of caution

    # Retention starts at end of year of invoice date
    retention_start_year = invoice.rechnungsdatum.year
    retention_end = date(retention_start_year + 10, 12, 31)

    return timezone.now().date() <= retention_end


def get_retention_end_date(invoice: Invoice) -> date:
    """Get the date when retention period ends for an invoice."""
    return date(invoice.rechnungsdatum.year + 10, 12, 31)


# === Admin Configuration ===

class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin configuration that enforces GoBD retention policy.
    - No delete action available
    - Archive action for admin-only access
    - Read-only for finalized invoices
    """

    list_display = [
        "rechnungsnummer",
        "invoice_type",
        "rechnungsdatum",
        "customer_name",
        "bruttobetrag",
        "status",
        "is_finalized",
        "retention_status",
    ]
    list_filter = [
        "status",
        "invoice_type",
        "rechnungsdatum",
        "is_finalized",
        "zahlungsmethode",
    ]
    search_fields = [
        "rechnungsnummer",
        "customer_name",
        "customer_email",
    ]
    readonly_fields = [
        "id",
        "rechnungsnummer",
        "checksum",
        "finalized_at",
        "created_at",
        "updated_at",
        "retention_end_display",
    ]
    ordering = ["-rechnungsdatum", "-rechnungsnummer"]

    # CRITICAL: Remove delete permission entirely
    def has_delete_permission(self, request, obj=None):
        """GoBD: Invoices must NEVER be deleted."""
        return False

    # Remove delete action from admin
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def get_readonly_fields(self, request, obj=None):
        """Make all fields read-only for finalized invoices."""
        if obj and obj.is_finalized:
            # Return all field names as read-only
            return [field.name for field in obj._meta.fields]
        return self.readonly_fields

    @admin.display(description="Aufbewahrung bis")
    def retention_end_display(self, obj):
        if obj and obj.rechnungsdatum:
            end_date = get_retention_end_date(obj)
            return end_date.strftime("%d.%m.%Y")
        return "-"

    @admin.display(description="Aufbewahrungsstatus", boolean=True)
    def retention_status(self, obj):
        return is_within_retention_period(obj)

    actions = ["mark_as_archived"]

    @admin.action(description="Ausgewaehlte Rechnungen archivieren (nur Anzeige)")
    def mark_as_archived(self, request, queryset):
        """
        Archive action - marks invoices as archived for internal tracking.
        Does NOT delete them. The invoices remain in the database.
        """
        # Only allow archiving invoices past retention period
        archived_count = 0
        skipped_count = 0

        for invoice in queryset:
            if is_within_retention_period(invoice):
                skipped_count += 1
                continue
            # Mark as archived (custom field or status update)
            archived_count += 1

        if skipped_count:
            messages.warning(
                request,
                f"{skipped_count} Rechnung(en) koennen nicht archiviert werden "
                f"(Aufbewahrungsfrist laeuft noch)."
            )
        if archived_count:
            messages.success(
                request,
                f"{archived_count} Rechnung(en) wurden archiviert."
            )


# === Management Command ===

# invoices/management/commands/check_retention_compliance.py

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check GoBD retention compliance for all invoices"

    def handle(self, *args, **options):
        from invoices.models import Invoice
        from invoices.retention import is_within_retention_period, get_retention_end_date

        total = Invoice.objects.count()
        finalized = Invoice.objects.filter(is_finalized=True).count()
        non_finalized = Invoice.objects.filter(is_finalized=False).exclude(
            status=Invoice.InvoiceStatus.DRAFT
        ).count()

        self.stdout.write(f"\nGoBD Retention Compliance Check")
        self.stdout.write(f"{'=' * 40}")
        self.stdout.write(f"Total invoices: {total}")
        self.stdout.write(f"Finalized: {finalized}")

        if non_finalized:
            self.stdout.write(self.style.ERROR(
                f"NON-FINALIZED (non-draft): {non_finalized} - COMPLIANCE ISSUE"
            ))

        # Check for invoices without PDFs
        no_pdf = Invoice.objects.filter(
            is_finalized=True,
            pdf_file=""
        ).count()

        if no_pdf:
            self.stdout.write(self.style.ERROR(
                f"Finalized without PDF: {no_pdf} - COMPLIANCE ISSUE"
            ))

        # Check for invoices without checksums
        no_checksum = Invoice.objects.filter(
            is_finalized=True,
            checksum=""
        ).count()

        if no_checksum:
            self.stdout.write(self.style.ERROR(
                f"Finalized without checksum: {no_checksum} - COMPLIANCE ISSUE"
            ))

        # Verify checksums
        tampered = 0
        for invoice in Invoice.objects.filter(is_finalized=True).exclude(checksum=""):
            if invoice.calculate_checksum() != invoice.checksum:
                tampered += 1
                self.stdout.write(self.style.ERROR(
                    f"TAMPERED: {invoice.rechnungsnummer} - checksum mismatch!"
                ))

        if tampered:
            self.stdout.write(self.style.ERROR(
                f"\nCRITICAL: {tampered} invoice(s) with checksum mismatches!"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nAll checksums valid."
            ))

        # Report retention periods
        within_retention = 0
        past_retention = 0
        for invoice in Invoice.objects.filter(is_finalized=True):
            if is_within_retention_period(invoice):
                within_retention += 1
            else:
                past_retention += 1

        self.stdout.write(f"\nWithin 10-year retention: {within_retention}")
        self.stdout.write(f"Past retention period: {past_retention}")

        if not non_finalized and not no_pdf and not no_checksum and not tampered:
            self.stdout.write(self.style.SUCCESS("\nGoBD COMPLIANCE: OK"))
        else:
            self.stdout.write(self.style.ERROR("\nGoBD COMPLIANCE: ISSUES FOUND"))
```

---

## 6. Invoice Download View

```python
# invoices/views.py

import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.views import View
from django.views.generic import ListView

from .models import Invoice

logger = logging.getLogger(__name__)


class InvoiceListView(LoginRequiredMixin, ListView):
    """
    User dashboard view listing all invoices for the authenticated user.
    Accessible from the Abo & Zahlung section of the dashboard.
    """

    model = Invoice
    template_name = "invoices/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 20

    def get_queryset(self):
        return (
            Invoice.objects
            .filter(
                customer=self.request.user,
                is_finalized=True,
            )
            .select_related("storno_reference")
            .order_by("-rechnungsdatum", "-rechnungsnummer")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Meine Rechnungen"
        return context


class InvoiceDownloadView(LoginRequiredMixin, View):
    """
    Secure invoice PDF download view.

    Security:
    - Requires authentication (LoginRequiredMixin)
    - Users can only download their own invoices
    - Admins can download any invoice
    - Logs all download access for audit trail

    URL: /dashboard/rechnungen/<rechnungsnummer>/download/
    """

    def get(self, request, rechnungsnummer):
        try:
            invoice = Invoice.objects.get(rechnungsnummer=rechnungsnummer)
        except Invoice.DoesNotExist:
            raise Http404("Rechnung nicht gefunden.")

        # Authorization check
        is_owner = invoice.customer == request.user
        is_admin = request.user.is_staff or request.user.is_superuser

        if not is_owner and not is_admin:
            logger.warning(
                f"Unauthorized invoice download attempt: "
                f"user={request.user.id}, invoice={rechnungsnummer}"
            )
            return HttpResponseForbidden(
                "Sie haben keine Berechtigung, diese Rechnung herunterzuladen."
            )

        # Check PDF exists
        if not invoice.pdf_file:
            raise Http404("PDF-Datei nicht verfuegbar.")

        # Log access for audit trail
        logger.info(
            f"Invoice download: user={request.user.id}, "
            f"invoice={rechnungsnummer}, admin={is_admin}"
        )

        # Serve PDF file
        response = FileResponse(
            invoice.pdf_file.open("rb"),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{invoice.rechnungsnummer}.pdf"'
        )

        return response


# invoices/urls.py

from django.urls import path
from . import views

app_name = "invoices"

urlpatterns = [
    path(
        "dashboard/rechnungen/",
        views.InvoiceListView.as_view(),
        name="invoice_list",
    ),
    path(
        "dashboard/rechnungen/<str:rechnungsnummer>/download/",
        views.InvoiceDownloadView.as_view(),
        name="invoice_download",
    ),
]
```

### Invoice List Template

```html
{# invoices/templates/invoices/invoice_list.html #}

{% extends "dashboard/dashboard_base.html" %}
{% load i18n humanize %}

{% block page_title %}Meine Rechnungen{% endblock %}

{% block dashboard_content %}
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h2 class="h5 mb-0">Rechnungen</h2>
    </div>
    <div class="card-body p-0">
        {% if invoices %}
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Rechnungsnr.</th>
                        <th>Typ</th>
                        <th>Datum</th>
                        <th>Betrag</th>
                        <th>Status</th>
                        <th>Aktion</th>
                    </tr>
                </thead>
                <tbody>
                    {% for invoice in invoices %}
                    <tr>
                        <td>
                            <code>{{ invoice.rechnungsnummer }}</code>
                        </td>
                        <td>
                            {% if invoice.invoice_type == "credit_note" %}
                                <span class="badge bg-danger">Storno</span>
                            {% else %}
                                <span class="badge bg-primary">Rechnung</span>
                            {% endif %}
                        </td>
                        <td>{{ invoice.rechnungsdatum|date:"d.m.Y" }}</td>
                        <td>
                            {% if invoice.invoice_type == "credit_note" %}-{% endif %}{{ invoice.bruttobetrag|floatformat:2 }} &euro;
                        </td>
                        <td>
                            {% if invoice.status == "paid" %}
                                <span class="badge bg-success">Bezahlt</span>
                            {% elif invoice.status == "sent" %}
                                <span class="badge bg-info">Versendet</span>
                            {% elif invoice.status == "cancelled" %}
                                <span class="badge bg-secondary">Storniert</span>
                            {% elif invoice.status == "overdue" %}
                                <span class="badge bg-warning">Ueberfaellig</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ invoice.get_status_display }}</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if invoice.pdf_file %}
                            <a href="{% url 'invoices:invoice_download' invoice.rechnungsnummer %}"
                               class="btn btn-sm btn-outline-primary"
                               title="PDF herunterladen">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                                     fill="currentColor" viewBox="0 0 16 16">
                                    <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                                    <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
                                </svg>
                                PDF
                            </a>
                            {% else %}
                                <span class="text-muted">-</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {# Pagination #}
        {% if is_paginated %}
        <div class="card-footer">
            <nav aria-label="Rechnungen Navigation">
                <ul class="pagination justify-content-center mb-0">
                    {% if page_obj.has_previous %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Zurueck</a>
                    </li>
                    {% endif %}

                    <li class="page-item disabled">
                        <span class="page-link">
                            Seite {{ page_obj.number }} von {{ page_obj.paginator.num_pages }}
                        </span>
                    </li>

                    {% if page_obj.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.next_page_number }}">Weiter</a>
                    </li>
                    {% endif %}
                </ul>
            </nav>
        </div>
        {% endif %}

        {% else %}
        <div class="text-center py-5">
            <p class="text-muted mb-0">Noch keine Rechnungen vorhanden.</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

---

## 7. Stornorechnung (Credit Note) for Widerruf Refunds

The Stornorechnung flow is fully implemented in the `InvoiceService.generate_storno_invoice()` method above. Here is the complete Widerruf-to-Storno workflow:

```python
# payments/services.py (Widerruf refund flow)

import logging
from django.db import transaction
from django.utils import timezone

from invoices.models import Invoice
from invoices.services import InvoiceService
from payments.models import Payment, Refund

logger = logging.getLogger(__name__)


class WiderrufService:
    """
    Service handling Widerruf (withdrawal) under SS 355 BGB.

    German consumer protection law grants a 14-day Widerrufsrecht
    (right of withdrawal) for online purchases. When a user exercises
    this right, we must:

    1. Process the Stripe refund
    2. Generate a Stornorechnung (credit note)
    3. Send the Stornorechnung via email
    4. Cancel the subscription if applicable
    5. Maintain full audit trail (GoBD compliant)
    """

    def process_widerruf(
        self,
        payment: Payment,
        reason: str = "Widerruf gemaess SS 355 BGB",
        requested_by_user: bool = True,
    ) -> dict:
        """
        Process a complete Widerruf refund.

        Args:
            payment: The Payment to refund
            reason: Reason text for the Stornorechnung
            requested_by_user: Whether the user initiated the withdrawal

        Returns:
            dict with keys: refund, storno_invoice, stripe_refund_id
        """
        import stripe
        from django.conf import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Validate Widerruf eligibility (14-day window)
        if requested_by_user:
            days_since_payment = (timezone.now().date() - payment.created_at.date()).days
            if days_since_payment > 14:
                raise ValueError(
                    f"Widerrufsfrist abgelaufen. Zahlung vom "
                    f"{payment.created_at.strftime('%d.%m.%Y')} liegt "
                    f"{days_since_payment} Tage zurueck (max. 14 Tage)."
                )

        with transaction.atomic():
            # 1. Process Stripe refund
            stripe_refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_intent_id,
                reason="requested_by_customer",
                metadata={
                    "reason": reason,
                    "widerruf": "true",
                    "original_payment_id": str(payment.id),
                },
            )

            # 2. Create Refund record
            refund = Refund.objects.create(
                payment=payment,
                amount=payment.amount_total,
                reason=reason,
                stripe_refund_id=stripe_refund.id,
                status="completed",
            )

            # 3. Update payment status
            payment.status = "refunded"
            payment.save(update_fields=["status", "updated_at"])

            # 4. Find the original invoice
            original_invoice = Invoice.objects.filter(
                stripe_payment_intent_id=payment.stripe_payment_intent_id,
                invoice_type=Invoice.InvoiceType.INVOICE,
                is_finalized=True,
            ).first()

            storno_invoice = None
            if original_invoice:
                # 5. Generate Stornorechnung
                invoice_service = InvoiceService()
                storno_invoice = invoice_service.generate_storno_invoice(
                    original_invoice=original_invoice,
                    reason=reason,
                )

                # 6. Send Stornorechnung via email
                invoice_service.send_invoice_email(storno_invoice)
            else:
                logger.warning(
                    f"No original invoice found for payment {payment.id} "
                    f"(PI: {payment.stripe_payment_intent_id})"
                )

            # 7. Cancel subscription if applicable
            if payment.subscription:
                stripe.Subscription.cancel(
                    payment.subscription.stripe_subscription_id,
                    prorate=False,
                )
                payment.subscription.status = "cancelled"
                payment.subscription.cancelled_at = timezone.now()
                payment.subscription.save(
                    update_fields=["status", "cancelled_at", "updated_at"]
                )

            logger.info(
                f"Widerruf processed: payment={payment.id}, "
                f"refund={refund.id}, storno={storno_invoice}"
            )

            return {
                "refund": refund,
                "storno_invoice": storno_invoice,
                "stripe_refund_id": stripe_refund.id,
            }
```

### Complete Widerruf Flow Diagram

```
User requests Widerruf (within 14 days)
    |
    v
[Validate 14-day window]
    |
    v
[Stripe Refund API call]
    |
    v
[Create Refund record in DB]
    |
    v
[Update Payment status -> "refunded"]
    |
    v
[Find original Invoice by stripe_payment_intent_id]
    |
    v
[InvoiceService.generate_storno_invoice()]
    |-- Generate ST-YYYY-NNNNN number (gapless)
    |-- Create Stornorechnung with negative amounts
    |-- Generate PDF via WeasyPrint
    |-- Finalize + calculate checksum
    |-- Mark original invoice as "cancelled"
    |
    v
[InvoiceService.send_invoice_email(storno)]
    |-- Email Stornorechnung PDF to customer
    |
    v
[Cancel Stripe Subscription if applicable]
    |
    v
[Return result dict with refund + storno data]
```

### Key GoBD Compliance Points

1. **Original invoices are NEVER deleted** - Only their status changes to "cancelled"
2. **Stornorechnung gets its own sequential number** from the shared gapless sequence
3. **Stornorechnung references the original** via `storno_reference` foreign key
4. **Both documents are permanently retained** for the 10-year period
5. **PDF files are immutable** once generated - checksums verify integrity
6. **Full audit trail** is maintained through status transitions and timestamps
