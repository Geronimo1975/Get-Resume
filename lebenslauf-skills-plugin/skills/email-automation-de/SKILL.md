---
name: email-automation-de
description: >
  This skill should be used when the user asks to "send application emails",
  "set up email automation", "connect Gmail", "configure SMTP",
  "track email responses", "monitor inbox", "classify email replies",
  "implement email sending", or mentions email automation, Gmail API, SMTP,
  email sending, email tracking, response monitoring, IMAP polling,
  email classification, application email, Bewerbung per Email,
  email credentials, or any email-related automation feature.
  Triggers on: email, Gmail, SMTP, IMAP, email sending, email tracking,
  response monitoring, inbox polling, email classification, application email,
  email credentials, OAuth, email automation.
---

# Email Automation (German Market)

Automated professional application email sending and response tracking. Emails sent from user's own account (Gmail OAuth / SMTP) for deliverability and legal compliance.

## Architecture

- **User's own email account** — emails sent from user's Gmail/SMTP (not platform domain)
- **Gmail OAuth2** — preferred, provides both sending (SMTP) and reading (IMAP)
- **Custom SMTP** — alternative for non-Gmail users
- **IMAP polling** — Celery periodic task checks for replies
- **Claude API** — classifies email responses into pipeline states
- **Django DRF** — API endpoints for credential management and sending

## Why User's Own Account?

1. **Deliverability**: Emails from user's real address, not a SaaS domain
2. **Legal (UWG §7)**: User takes responsibility for email content
3. **Trust**: Recipients see a real person, not a bot
4. **Replies come to user**: Natural email thread in their inbox

## Email Credential Flow

```
1. User connects Gmail in Vue.js dashboard:
   → Click "Gmail verbinden" → OAuth2 consent screen
   → Scopes: gmail.send + gmail.readonly
   → Callback stores encrypted OAuth tokens

2. Alternative: User enters SMTP credentials:
   → Host, port, username, password (encrypted at rest)
   → Verification: send test email to self
   → POST /api/v1/users/me/email-credentials/
```

## Sending Flow

```
1. User clicks "Bewerbung senden" on a job in pipeline
   → Vue.js shows email preview modal:
     - Subject: "Bewerbung als {Position} — {Name}"
     - Body: Professional email template
     - Attachments: CV PDF + Cover Letter PDF
     - To: job.contact_email or company email

2. User reviews/edits → confirms send
   → POST /api/v1/applications/{id}/send-email/

3. Django dispatches Celery task: send_application_email
   → Loads user's encrypted email credentials
   → Constructs MIME email with attachments
   → Sends via Gmail API or SMTP
   → Creates ApplicationEmail record (direction=sent)
   → Updates JobApplication status → "applied"

4. Email template (professional German):
"""
Betreff: Bewerbung als {Position} bei {Company}

Sehr geehrte Damen und Herren,

anbei übersende ich Ihnen meine Bewerbungsunterlagen für die
ausgeschriebene Stelle als {Position}.

Meine vollständigen Bewerbungsunterlagen finden Sie im Anhang:
- Lebenslauf
- Bewerbungsschreiben

Ich freue mich auf Ihre Rückmeldung und stehe für ein
persönliches Gespräch gerne zur Verfügung.

Mit freundlichen Grüßen
{Name}
{Phone}
{Email}
"""
```

## Response Monitoring

```
Celery periodic task: check_email_responses (every 15 minutes)

1. For each user with active applications:
   → Load Gmail OAuth credentials
   → IMAP search: emails FROM domains of applied companies
   → Filter by date (since last check)

2. For each new reply:
   → Extract text content
   → Claude API classification:
     - "rejection" → "Leider müssen wir Ihnen mitteilen..."
     - "interview" → "Wir laden Sie herzlich ein..."
     - "follow_up" → "Könnten Sie uns noch... zusenden?"
     - "offer" → "Wir freuen uns, Ihnen... anzubieten"
     - "other" → Unclassified

3. Create ApplicationEmail record (direction=received)
4. Update JobApplication status based on classification
5. Notify user via dashboard + optional email notification
```

## Django Models

### EmailCredential
```python
class EmailCredential(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(choices=[
        ('gmail', 'Gmail (OAuth2)'),
        ('smtp', 'Custom SMTP'),
        ('outlook', 'Outlook (OAuth2)'),
    ])
    email_address = models.EmailField()
    oauth_token = EncryptedTextField(blank=True)      # OAuth refresh token
    smtp_host = EncryptedCharField(max_length=200, blank=True)
    smtp_port = models.IntegerField(default=587)
    smtp_username = EncryptedCharField(max_length=200, blank=True)
    smtp_password = EncryptedCharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/users/me/email-credentials/` | GET | List credentials |
| `/api/v1/users/me/email-credentials/` | POST | Add SMTP credential |
| `/api/v1/users/me/email-credentials/gmail/` | POST | Gmail OAuth callback |
| `/api/v1/users/me/email-credentials/{id}/verify/` | POST | Send test email |
| `/api/v1/users/me/email-credentials/{id}/` | DELETE | Remove credential |
| `/api/v1/applications/{id}/send-email/` | POST | Send application email |
| `/api/v1/applications/check-responses/` | POST | Trigger response check |

## Anti-Spam Measures

- Random delay between sends: 30s – 5min (configurable)
- Maximum 20 emails per day (Premium) / 50 per day (Business)
- No duplicate sends to same email within 30 days
- Human-like send patterns (not all at once)
- Respect business hours: send between 08:00–18:00 Europe/Berlin

## Rate Limits

| Plan | Emails/month | Emails/day |
|------|-------------|-----------|
| Kostenlos | 0 | 0 |
| Premium | 20 | 5 |
| Business | 200 | 50 |

## Security

- OAuth tokens and SMTP passwords encrypted at rest (django-encrypted-model-fields)
- OAuth tokens refreshed automatically before expiry
- User can revoke Gmail access at any time
- Credentials never exposed via API response (write-only fields)
- IMAP read access only checks for replies from applied companies (not full inbox scan)
