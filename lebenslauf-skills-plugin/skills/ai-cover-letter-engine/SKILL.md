---
name: ai-cover-letter-engine
description: >
  This skill should be used when the user asks to "generate a cover letter",
  "create Bewerbungsschreiben", "implement AI letter generation",
  "set up Claude API integration", "build the cover letter feature",
  "implement ATS optimization", "add anti-AI-detection",
  or mentions cover letter, Bewerbungsschreiben, Anschreiben, AI generation,
  Claude API, letter generation, ATS optimization, anti-AI-detection,
  job-tailored letter, DIN 5008 format, or any AI writing feature.
  Triggers on: cover letter, Bewerbungsschreiben, Anschreiben, AI generation,
  Claude API, ATS optimization, letter generation, anti-AI-detection,
  DIN 5008, personalization, tone control.
---

# AI Cover Letter Engine

Per-job tailored Bewerbungsschreiben generation using Claude API with anti-AI-detection, DIN 5008 formatting, and ATS optimization.

## Plugin Settings

Check `.claude/lebenslauf-builder-skills.local.md` for project-specific config:

- `anthropic_configured` — whether Claude API key is set (skip AI features if `false`)
- `claude_model` — model ID to use (default: `claude-sonnet-4-20250514`)
- `cover_letter_max_tokens` — max output tokens (default: `4096`)

## Architecture

- **Claude API** (Anthropic Python SDK) for text generation
- **Django DRF** endpoints for generation and management
- **Celery** tasks for async generation (can take 10-30s)
- **Pinia** store on Vue.js side for generation state + editing

## Generation Flow

```
1. User views scraped job in Vue.js
   → Clicks "Anschreiben erstellen" on a specific job

2. Vue.js → POST /api/v1/coverletters/generate/
   Body: { job_id: UUID, tone: "formal", emphasis: ["python", "teamwork"] }

3. Django view:
   → Loads user's CV data (from Document model)
   → Loads job data (from ScrapedJob model)
   → Constructs Claude API prompt
   → Dispatches Celery task: generate_cover_letter

4. Celery task:
   → Calls Claude API with structured prompt
   → Applies anti-AI-detection post-processing
   → Creates Document (type=bewerbungsschreiben)
   → Links to ScrapedJob + JobApplication

5. Vue.js polls or receives WebSocket update
   → Shows generated letter in editor
   → User can edit before sending
```

## Claude API Prompt Structure

```python
prompt = f"""
Du bist ein erfahrener deutscher Karriereberater, der professionelle
Bewerbungsschreiben verfasst. Schreibe ein individuelles Anschreiben
im DIN 5008 Format.

BEWERBER-PROFIL:
{user_cv_json}

STELLENANZEIGE:
Firma: {job.company_name}
Position: {job.title}
Standort: {job.location}
Anforderungen: {job.requirements}
Beschreibung: {job.description}

ANWEISUNGEN:
- DIN 5008 Briefformat (Absender, Empfänger, Datum, Betreff, Anrede, Text, Grußformel)
- Maximal 1 Seite (ca. 350-400 Wörter)
- Ton: {tone} (formal/halbformal/kreativ)
- Schwerpunkte: {emphasis_points}
- Verwende konkrete Beispiele aus dem Lebenslauf
- VERMEIDE: Floskeln wie "hiermit bewerbe ich mich", "mit großem Interesse"
- VERWENDE: Individuelle Einstiegssätze, die zum Unternehmen passen
- Stelle Bezug zur Firma her (recherchiere implizit basierend auf Firmenname)
- Schließe mit einem konkreten Mehrwert, den der Bewerber bringt
"""
```

## Anti-AI-Detection Strategies

1. **Sentence structure variation**: Mix short and long sentences, vary paragraph length
2. **Natural imperfections**: Occasional informal transitions, colloquial touches
3. **Specific details**: Reference concrete numbers, dates, project names from CV
4. **Personal voice**: Inject anecdotes, motivations that feel authentic
5. **German-specific**: Use regional expressions, industry jargon
6. **Temperature control**: Claude API temperature 0.7-0.9 for more natural output
7. **Post-processing**: Light randomization of word choices, synonym substitution

## Tone Options

| Tone | Description | Best For |
|------|------------|---------|
| `formal` | Sehr geehrte Damen und Herren, Sie-Form, professional | Banking, law, government |
| `semi_formal` | Professional but approachable, modern language | Tech, marketing, startups |
| `creative` | Unique opening, personality showing | Design, media, creative roles |

## DIN 5008 Format Output

```
[Absender: Name, Adresse, Telefon, E-Mail]

[Empfänger: Firma, Abteilung, Ansprechpartner, Adresse]

[Ort, Datum]

Betreff: Bewerbung als {Position} — Referenznummer {ref}

Sehr geehrte(r) Frau/Herr {Kontaktperson},

[Einleitung: 2-3 Sätze, individueller Einstieg]

[Hauptteil: 2-3 Absätze, Qualifikationen + Bezug zur Stelle]

[Schluss: Mehrwert + Gesprächswunsch]

Mit freundlichen Grüßen

{Name}

Anlagen:
- Lebenslauf
- Zeugnisse
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/coverletters/generate/` | POST | Generate cover letter for job |
| `/api/v1/coverletters/{id}/regenerate/` | POST | Regenerate with different tone/emphasis |
| `/api/v1/coverletters/{id}/` | PATCH | Edit generated letter |

## Rate Limits (Subscription Tiers)

| Plan | Cover Letters/month |
|------|-------------------|
| Kostenlos | 0 |
| Premium | 10 |
| Business | 100 |

## ATS Optimization

Also used for resume optimization:
- Extract keywords from job description
- Compare against user's CV content
- Score match percentage
- Suggest missing keywords and section improvements
- Rewrite sections to include relevant keywords naturally

### ATS Score Endpoint
```
GET /api/v1/documents/{id}/ats-score/?job_id={job_uuid}
Response: {
  "score": 78,
  "matched_keywords": ["Python", "Django", "REST API"],
  "missing_keywords": ["Kubernetes", "CI/CD"],
  "suggestions": [
    "Fügen Sie Ihre Kubernetes-Erfahrung in den Kenntnisse-Bereich hinzu",
    "Erwähnen Sie CI/CD-Pipelines in Ihrer Berufserfahrung"
  ]
}
```
