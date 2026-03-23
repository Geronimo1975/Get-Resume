Ești un expert în Django care se specializează în implementarea sistemelor complete de autentificare. Sarcina ta este să construiești o soluție end-to-end de înregistrare, confirmare email și autentificare, cu sincronizare către Brevo CRM și stocarea în PostgreSQL.

## Obiectivul

Implementează și verifică funcționarea completă a următorului flux:
1. Utilizator nou se înregistrează cu email și parolă
2. Primește email de confirmare via Brevo (cu link de validare)
3. Confirmă înregistrarea prin link-ul din email
4. Se loghează cu credențialele sale
5. Accesează dashboardul utilizatorului (pagină protejată)
6. Datele apar corect în Django Admin
7. Contactul este sincronizat în Brevo CRM
8. Toate informațiile sunt stocate în PostgreSQL cu timestamp-uri și status-uri

## Ceea ce trebuie să implementezi

### Modelul User
- Extensie personalizată a User-ului Django cu: `email_confirmed` (boolean), `confirmation_token` (string unic), `confirmation_token_expiry` (datetime)
- Timestamps: `created_at`, `confirmed_at`

### Formularul de înregistrare
- Validare email (format corect, nu duplicat)
- Validare parolă (minim 8 caractere, complexitate)
- Mesaje de eroare clare pentru utilizator

### Sistemul de confirmare email
- Token unic generat la înregistrare (minim 32 caractere, random)
- Token expiră după 24 de ore
- Email trimis via Brevo API cu template personalizat, conținând link-ul de confirmare
- Rută de confirmare care validează token-ul și expirarea acestuia
- După confirmare, utilizatorul este marcat ca `email_confirmed=True`

### Autentificare și login
- Sistem de sesiuni Django standard
- Login validează că emailul este confirmat (acces refuzat dacă nu e confirmat)
- Redirect automat la dashboard după login reușit
- Protecție CSRF pe toate formularele
- Rate limiting pe înregistrare și login (max 5 tentative/IP pe 15 minute)

### Integrarea Brevo CRM
- API call la Brevo pentru a crea/actualiza contact atunci când utilizatorul se înregistrează
- Datele trimise: email, nume, dată înregistrare, status confirmare (confirmed_at)
- Error handling dacă API-ul Brevo nu răspunde (logging, retry logic)

### Django Admin
- Utilizatorii sunt vizibili cu toți câmpurile relevante
- Filtru pentru utilizatori confirmed/unconfirmed
- Câmpurile `email` și `confirmation_token` sunt readonly
- Display custom pentru a arăta clar status confirmării

### Dashboard utilizator
- Pagină protejată cu `@login_required` care afișează informațiile utilizatorului logat
- Informații afișate: email, dată înregistrare, status confirmare, dată confirmării
- Buton de logout

## Cerințe tehnice

- **Production-ready**: error handling complet, validare pe toate nivelele, try-catch pentru API calls
- **Securitate**: CSRF tokens, rate limiting, token-uri random, expiră de token-uri
- **Stocarea datelor**: Migrations Django pentru toate modelele, timestamps în UTC
- **Automatizare**: Folosește Django signals pentru a declanșa sincronizarea Brevo automat după înregistrare
- **Testare**: Codul trebuie să fie testabil; oferă instrucțiuni clare pentru a verifica manual fiecare pas al fluxului
- **Django 5.x / Python 3.12+**

## Livrabil

Oferă:
- `models.py` – Modelul User personalizat
- `forms.py` – Formulare de înregistrare și login
- `views.py` – Vederile pentru înregistrare, confirmare, login, dashboard
- `urls.py` – Rutele pentru toate acțiunile
- `templates/` – HTML-uri pentru signup, confirmation (mesaj de success), login, dashboard
- `settings.py` – Actualizări necesare (email backend, Brevo API key, CSRF settings)
- `signals.py` sau logica în views – Sincronizare Brevo la înregistrare
- Instrucțiuni clare de:
  - Configurare Brevo API key și template ID
  - Rulare migrații
  - Testare end-to-end (pas cu pas prin tot fluxul)
  - Verificare în Django Admin și Brevo CRM

Dacă sunt erori sau lipsuri în implementare, identific-le și ofer soluții. Codul trebuie să fie gata de produs – nu prototip.