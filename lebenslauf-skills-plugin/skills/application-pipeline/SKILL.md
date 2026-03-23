---
name: application-pipeline
description: >
  This skill should be used when the user asks to "track applications",
  "build the pipeline", "create Kanban board", "implement application tracking",
  "show application status", "build Bewerbungen view", "add pipeline analytics",
  "classify responses", or mentions application pipeline, Kanban, application tracking,
  Bewerbungen, application status, response classification, pipeline analytics,
  interview tracking, job application state, or any application lifecycle feature.
  Triggers on: pipeline, Kanban, application tracking, Bewerbungen, application status,
  interview, rejection, follow-up, offer, response classification, pipeline analytics,
  application card, job application.
---

# Application Pipeline

Track every job application through its lifecycle — from discovery to offer — with Kanban board, response classification, and analytics.

## Architecture

- **Django DRF** API for application CRUD and status management
- **Vue.js** Kanban board (vue-draggable-plus) and table views
- **Claude API** for automatic email response classification
- **Celery** periodic task for IMAP response monitoring
- **Chart.js** for pipeline analytics

## Application States

```
discovered → applied → waiting → rejected
                                → interview → follow_up
                                             → offer
```

| State | Description | Trigger |
|-------|------------|---------|
| `discovered` | Job found via scraping, not yet applied | User clicks "Merken" on a job |
| `applied` | Application email sent | After email sent successfully |
| `waiting` | Waiting for response | Auto-set after sending |
| `rejected` | Company declined | AI classified or manual |
| `interview` | Invited to interview | AI classified or manual |
| `follow_up` | Company wants more info | AI classified or manual |
| `offer` | Job offer received | AI classified or manual |

## Vue.js Components

### Kanban Board (Primary View)
```
src/components/pipeline/
├── KanbanBoard.vue         # Draggable columns layout
├── KanbanColumn.vue        # Single status column
├── ApplicationCard.vue     # Card with job info + actions
├── ApplicationDetail.vue   # Full detail modal/drawer
├── PipelineStats.vue       # Analytics dashboard
├── PipelineTable.vue       # Alternative table view
└── PipelineFilters.vue     # Filter bar
```

### Kanban Layout
```
┌────────────────────────────────────────────────────────────────┐
│  Pipeline: [Kanban ▣] [Tabelle ≡]  Filters: [Platform ▼]     │
│            [Zeitraum ▼] [Suche...]                            │
├───────────┬───────────┬───────────┬───────────┬───────────────┤
│ Gemerkt   │ Beworben  │ Warten    │ Interview │ Angebot       │
│ (12)      │ (8)       │ (5)       │ (2)       │ (1)           │
│           │           │           │           │               │
│ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────┐ │ ┌───────────┐ │
│ │ Job 1 │ │ │ Job 4 │ │ │ Job 9 │ │ │Job 14 │ │ │ Job 18    │ │
│ │ SAP   │ │ │ BMW   │ │ │ Bosch │ │ │Siemens│ │ │ Allianz   │ │
│ │ Berlin│ │ │München│ │ │ Stuttg│ │ │München│ │ │ München   │ │
│ └───────┘ │ └───────┘ │ └───────┘ │ └───────┘ │ └───────────┘ │
│ ┌───────┐ │ ┌───────┐ │           │           │               │
│ │ Job 2 │ │ │ Job 5 │ │           │           │               │
│ └───────┘ │ └───────┘ │           │           │               │
└───────────┴───────────┴───────────┴───────────┴───────────────┘
│           Abgelehnt (3) — collapsed                            │
└────────────────────────────────────────────────────────────────┘
```

### Application Card Content
- Company name + logo (if available)
- Job title
- Location + remote badge
- Platform badge (LinkedIn / Indeed / StepStone)
- Days since last action
- Status badge (color-coded)
- Quick actions: Open job link, Edit notes, Move status

### Application Detail (Drawer/Modal)
- Full job description
- Applied date + response timeline
- Email thread (sent + received)
- Cover letter used (link to editor)
- CV used (link to editor)
- Notes (free text)
- Interview date + reminder
- Manual status change buttons

## Django Models

### JobApplication
```python
class JobApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('jobs.ScrapedJob', on_delete=models.CASCADE)
    document = models.ForeignKey('documents.Document', null=True, on_delete=models.SET_NULL)
    cover_letter = models.ForeignKey('documents.Document', null=True, on_delete=models.SET_NULL, related_name='applications_as_cl')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='discovered')
    applied_at = models.DateTimeField(null=True)
    response_at = models.DateTimeField(null=True)
    interview_date = models.DateTimeField(null=True)
    notes = models.TextField(blank=True)
    reminder_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### ApplicationEmail
```python
class ApplicationEmail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='emails')
    direction = models.CharField(choices=[('sent', 'Sent'), ('received', 'Received')])
    subject = models.CharField(max_length=500)
    body = models.TextField()
    from_email = models.EmailField()
    to_email = models.EmailField()
    attachments = models.JSONField(default=list)
    message_id = models.CharField(max_length=500, blank=True)
    sent_at = models.DateTimeField(null=True)
    received_at = models.DateTimeField(null=True)
    classification = models.CharField(
        max_length=20, blank=True,
        choices=[('rejection', 'Absage'), ('interview', 'Einladung'),
                 ('follow_up', 'Nachfrage'), ('offer', 'Angebot'), ('other', 'Sonstiges')]
    )
    classified_by = models.CharField(max_length=10, choices=[('ai', 'AI'), ('manual', 'Manual')], blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/applications/` | GET | List all applications (filterable) |
| `/api/v1/applications/` | POST | Create application (save job to pipeline) |
| `/api/v1/applications/{id}/` | GET | Application detail with emails |
| `/api/v1/applications/{id}/` | PATCH | Update status, notes, interview date |
| `/api/v1/applications/{id}/send-email/` | POST | Send application email |
| `/api/v1/applications/stats/` | GET | Pipeline analytics |
| `/api/v1/applications/check-responses/` | POST | Trigger email check |

## Pipeline Analytics

```
GET /api/v1/applications/stats/
Response: {
  "total": 28,
  "by_status": {
    "discovered": 12,
    "applied": 8,
    "waiting": 5,
    "rejected": 3,
    "interview": 2,
    "follow_up": 1,
    "offer": 1
  },
  "response_rate": 0.375,          // 6 responses out of 16 applied
  "avg_response_days": 8.5,
  "success_rate": 0.125,           // 2 interviews out of 16 applied
  "by_platform": {
    "linkedin": { "applied": 10, "response_rate": 0.4 },
    "indeed": { "applied": 4, "response_rate": 0.25 },
    "stepstone": { "applied": 2, "response_rate": 0.5 }
  },
  "weekly_activity": [
    { "week": "2026-W09", "applied": 5, "responses": 2 },
    { "week": "2026-W10", "applied": 3, "responses": 1 }
  ]
}
```

## Response Classification (Claude API)

```python
classification_prompt = """
Klassifiziere diese E-Mail-Antwort auf eine Bewerbung:

E-Mail Text:
{email_body}

Kategorien:
- "rejection": Absage, die Stelle wurde anderweitig besetzt
- "interview": Einladung zum Vorstellungsgespräch oder Telefoninterview
- "follow_up": Nachfrage nach zusätzlichen Unterlagen oder Informationen
- "offer": Stellenangebot oder Vertragsvorschlag
- "other": Automatische Antwort, Newsletter, oder irrelevant

Antworte NUR mit dem Kategorienamen.
"""
```
