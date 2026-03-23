# MCP Servers Download & Configuration Prompt
## Lebenslauf-Builder SaaS — Piața Germană

---

## Situația Curentă

### MCP Servers deja conectate în Claude.ai:
| Server | URL | Status |
|--------|-----|--------|
| Cloudflare Developer Platform | `https://bindings.mcp.cloudflare.com/sse` | ✅ Conectat |
| Canva | `https://mcp.canva.com/mcp` | ✅ Conectat |
| Indeed | `https://mcp.indeed.com/claude/mcp` | ✅ Conectat |
| Jotform | `https://mcp.jotform.com` | ✅ Conectat |
| Google Calendar | `https://gcal.mcp.claude.com/mcp` | ✅ Conectat |
| Gmail | `https://gmail.mcp.claude.com/mcp` | ✅ Conectat |
| n8n | `https://n8n.get-hub.io/mcp-server/http` | ✅ Conectat |

### Ce folosim din cele existente pentru proiect:
- **n8n** → Orchestrare workflow-uri, automatizări email, DSGVO automation
- **Cloudflare** → CDN, DNS, Workers pentru edge functions
- **Gmail** → Comunicare cu utilizatorii în faza de development
- **Google Calendar** → Project management, milestones
- **Indeed** → Integrare job listings (Phase 3)
- **Canva** → Marketing materials, social media assets
- **Jotform** → Formulare feedback beta users, surveys

---

## MCP Servers de Instalat

### Categorie 1: CRITICE (necesare inainte de Phase 1)

---

#### 1.1 Stripe MCP Server (OFICIAL)

**De ce:** Platforma de plati principala — checkout, subscriptii, facturi, SEPA, Giropay, refunds.

**Tip:** Remote MCP Server (hosted de Stripe, OAuth)

**URL Remote:**
```
https://mcp.stripe.com
```

**Alternativ Local (npx):**
```bash
npx -y @stripe/mcp --api-key=YOUR_STRIPE_SECRET_KEY
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp", "--api-key=sk_test_YOUR_KEY"],
      "env": {
        "STRIPE_API_KEY": "sk_test_YOUR_STRIPE_TEST_KEY"
      }
    }
  }
}
```

**Restricted API Key (RAK) permissions necesare:**
- Customers: Read + Write
- Products: Read + Write
- Prices: Read + Write
- Payment Intents: Read + Write
- Subscriptions: Read + Write (nu folosim subscription automata, dar pentru management)
- Invoices: Read + Write
- Refunds: Read + Write
- Checkout Sessions: Read + Write
- Webhook Endpoints: Read + Write
- Tax Rates: Read (pentru MwSt 19%)

**Setup:**
1. Acceseaza https://dashboard.stripe.com/apikeys
2. Creaza Restricted API Key cu permisiunile de mai sus
3. Configureaza in Claude Desktop sau Claude.ai
4. Test: intreba Claude "List my Stripe products" pentru verificare

**Stripe Test Tools (optional dar recomandat):**
```json
{
  "mcpServers": {
    "stripe-test": {
      "command": "npx",
      "args": ["stripe-test-mcp"],
      "env": {
        "STRIPE_API_KEY": "sk_test_YOUR_KEY"
      }
    }
  }
}
```
Acesta adauga test clocks, bulk customer creation, cleanup — foarte util pentru testarea fluxurilor de plata cu SEPA si Widerrufsrecht.

---

#### 1.2 PostgreSQL MCP Server

**De ce:** Baza de date principala — interogari directe, debugging, migrari, analize date.

**GitHub:** https://github.com/modelcontextprotocol/servers (official reference)

**Instalare:**
```bash
npm install -g @modelcontextprotocol/server-postgres
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@localhost:5432/lebenslauf_db"
      ]
    }
  }
}
```

**Alternativa via n8n (deja conectat):**
Poti crea un PostgreSQL MCP Server direct in n8n folosind template-ul:
https://n8n.io/workflows/3631-build-your-own-postgresql-mcp-server/

Avantaj: nu necesita instalare separata, se conecteaza prin n8n-ul deja configurat.

**Recomandare pentru productie:**
- Foloseste un read-only user pentru MCP queries
- Connection string cu SSL: `postgresql://readonly:pass@host:5432/lebenslauf_db?sslmode=require`
- NU expune write access prin MCP in production

---

#### 1.3 GitHub MCP Server

**De ce:** Repo management, code review, issues tracking, CI/CD triggers, PR management.

**URL Remote (OAuth):**
```
https://github.com/modelcontextprotocol/servers
```

**Instalare:**
```bash
npm install -g @modelcontextprotocol/server-github
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN"
      }
    }
  }
}
```

**Token permissions necesare:**
- repo (full control)
- workflow (GitHub Actions)
- read:org (daca folosesti organizatie)

---

### Categorie 2: IMPORTANTE (necesare la Phase 2)

---

#### 2.1 Sentry MCP Server

**De ce:** Error tracking, performance monitoring, issue management in productie.

**URL Remote:**
```
https://mcp.sentry.dev/sse
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "sntrys_YOUR_TOKEN",
        "SENTRY_ORG": "your-org-slug"
      }
    }
  }
}
```

**Util pentru:**
- Query errors direct din Claude: "Show me all unresolved errors from last 24h"
- Generate patches pentru bugs: "Fix the TypeError in payments/views.py"
- Performance monitoring: "What are the slowest endpoints?"

---

#### 2.2 Puppeteer MCP Server

**De ce:** Browser automation — testare automata UI, screenshot template previews, E2E testing.

**Instalare:**
```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

**Use cases proiect:**
- Generare screenshot-uri automate pentru template previews
- Testare cookie consent banner flow (click "Einstellungen" → toggle → verify)
- E2E test checkout flow cu Stripe test mode
- Verificare Impressum accessibility (2 click rule)

---

#### 2.3 Filesystem MCP Server

**De ce:** Acces la fisierele proiectului local — edit cod, citire configuratii, management assets.

**Instalare:**
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/lebenslauf-builder"
      ]
    }
  }
}
```

**IMPORTANT:** Specifica DOAR directorul proiectului, nu root filesystem.

---

#### 2.4 Git MCP Server

**De ce:** Git operations directe — branch management, commit history, diff analysis, blame.

**Instalare:**
```bash
npm install -g @modelcontextprotocol/server-git
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    }
  }
}
```

---

### Categorie 3: NICE TO HAVE (Phase 3+)

---

#### 3.1 Memory MCP Server

**De ce:** Persistent memory pentru context proiect — decizii arhitecturale, conventions, learnings.

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Util pentru:** Stocare knowledge graph cu decizii de design, naming conventions german, legal requirements checklist.

---

#### 3.2 Fetch MCP Server

**De ce:** Web content fetching — research competitori, monitorizare preturi, scraping job data.

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

---

#### 3.3 Sequential Thinking MCP Server

**De ce:** Complex reasoning pentru arhitectura decizii, debugging complex flows, planning.

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## MCP Servers Custom de Construit (prin n8n)

Pe langa MCP servers pre-built, vom construi servere custom prin n8n (deja conectat) pentru workflow-uri specifice proiectului:

### Custom 1: Lebenslauf PDF Generator MCP
**Scop:** Trigger PDF generation din orice MCP client
**Implementare:** n8n workflow cu MCP Trigger → Django API call → WeasyPrint → return PDF URL
```
n8n workflow:
  MCP Trigger (tool: generate_lebenslauf_pdf)
  → HTTP Request (POST /api/documents/{id}/generate-pdf/)
  → Wait for response
  → Return PDF download URL
```

### Custom 2: DSGVO Compliance Checker MCP
**Scop:** Verifica conformitatea DSGVO a unei pagini/feature
**Implementare:** n8n workflow care auditeaza cookie consent, privacy policy, Impressum
```
n8n workflow:
  MCP Trigger (tool: check_gdpr_compliance)
  → Puppeteer: load page
  → Check: cookie banner present before tracking?
  → Check: Impressum link in footer?
  → Check: Datenschutz link accessible?
  → Return compliance report JSON
```

### Custom 3: Invoice Generator MCP
**Scop:** Generare factura GoBD din orice context
**Implementare:** n8n workflow care genereaza PDF factura conform GoBD
```
n8n workflow:
  MCP Trigger (tool: generate_invoice)
  → Query Stripe payment data
  → Apply GoBD template (Rechnungsnummer, MwSt, etc.)
  → Generate PDF via Django endpoint
  → Store + return URL
```

### Custom 4: Template Preview Generator MCP
**Scop:** Generare preview screenshots pentru template catalog
**Implementare:** n8n workflow cu Puppeteer pentru screenshot automation
```
n8n workflow:
  MCP Trigger (tool: generate_template_preview)
  → Load template with sample data
  → Puppeteer screenshot (A4 dimensions)
  → Resize + optimize image
  → Upload to CDN
  → Return image URL
```

---

## Ordinea de Instalare

### Prioritate IMEDIATA (inainte de scriere cod):
```
1. Stripe MCP          → Testare plati de la inceput
2. PostgreSQL MCP      → Database access direct
3. GitHub MCP          → Repo setup + management
4. Filesystem MCP      → File management proiect
5. Git MCP             → Version control
```

### Prioritate Phase 2:
```
6. Sentry MCP          → Error tracking in staging/prod
7. Puppeteer MCP       → Automated testing + screenshots
```

### Prioritate Phase 3:
```
8. Memory MCP          → Knowledge persistence
9. Fetch MCP           → Web research automation
10. Sequential Thinking → Complex reasoning tasks
```

### Custom MCP via n8n (se construiesc pe parcurs):
```
11. PDF Generator       → Cand editorul e functional
12. DSGVO Checker       → Inainte de lansare
13. Invoice Generator   → Cand platile sunt live
14. Template Preview    → Cand template catalog e gata
```

---

## Script Instalare Batch (toate serverele pre-built)

```bash
#!/bin/bash
# install_mcp_servers.sh
# Instaleaza toate MCP servers necesare pentru Lebenslauf-Builder

echo "=== Installing MCP Servers for Lebenslauf-Builder ==="

# Official MCP Reference Servers
echo "[1/7] Installing PostgreSQL MCP..."
npm install -g @modelcontextprotocol/server-postgres

echo "[2/7] Installing GitHub MCP..."
npm install -g @modelcontextprotocol/server-github

echo "[3/7] Installing Filesystem MCP..."
npm install -g @modelcontextprotocol/server-filesystem

echo "[4/7] Installing Git MCP..."
npm install -g @modelcontextprotocol/server-git

echo "[5/7] Installing Puppeteer MCP..."
npm install -g @modelcontextprotocol/server-puppeteer

echo "[6/7] Installing Memory MCP..."
npm install -g @modelcontextprotocol/server-memory

echo "[7/7] Installing Fetch MCP..."
npm install -g @modelcontextprotocol/server-fetch

# Stripe (runs via npx, no global install needed)
echo "[Stripe] Verifying Stripe MCP availability..."
npx -y @stripe/mcp --help 2>/dev/null && echo "Stripe MCP OK" || echo "Stripe MCP will download on first use"

# Sentry (runs via npx)
echo "[Sentry] Verifying Sentry MCP availability..."
npx -y @sentry/mcp-server --help 2>/dev/null && echo "Sentry MCP OK" || echo "Sentry MCP will download on first use"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure claude_desktop_config.json with connection strings"
echo "2. Set environment variables (STRIPE_API_KEY, GITHUB_TOKEN, etc.)"
echo "3. Test each server: 'List my Stripe products', 'Show tables in database', etc."
```

---

## Claude Desktop Config Complet

Fisierul complet `claude_desktop_config.json` cu toate serverele:

```json
{
  "mcpServers": {
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp", "--api-key=sk_test_YOUR_KEY"],
      "env": {
        "STRIPE_API_KEY": "sk_test_YOUR_STRIPE_TEST_KEY"
      }
    },
    "stripe-test-tools": {
      "command": "npx",
      "args": ["stripe-test-mcp"],
      "env": {
        "STRIPE_API_KEY": "sk_test_YOUR_KEY"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://lebenslauf_user:PASSWORD@localhost:5432/lebenslauf_db"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/YOUR_USER/projects/lebenslauf-builder"
      ]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "sntrys_YOUR_TOKEN",
        "SENTRY_ORG": "lebenslauf-builder"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## Environment Variables Template (.env.mcp)

```bash
# === MCP Server Environment Variables ===
# Copiaza in .env si completeaza cu valorile tale

# Stripe
STRIPE_API_KEY=sk_test_XXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXX

# PostgreSQL
DATABASE_URL=postgresql://lebenslauf_user:XXXXX@localhost:5432/lebenslauf_db
DATABASE_READONLY_URL=postgresql://readonly_user:XXXXX@localhost:5432/lebenslauf_db

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_XXXXX

# Sentry
SENTRY_AUTH_TOKEN=sntrys_XXXXX
SENTRY_ORG=lebenslauf-builder
SENTRY_PROJECT=lebenslauf-django

# n8n (deja conectat)
N8N_API_URL=https://n8n.get-hub.io/api/v1
N8N_API_KEY=XXXXX

# Filesystem (path-ul proiectului local)
PROJECT_PATH=/home/YOUR_USER/projects/lebenslauf-builder
```

---

## Securitate MCP — Reguli de Bază

1. **NU folosi live Stripe keys in MCP** — doar `sk_test_` keys
2. **PostgreSQL MCP** — foloseste DOAR read-only user in production
3. **Filesystem MCP** — restrictioneaza la directorul proiectului, niciodata root
4. **GitHub tokens** — foloseste fine-grained tokens cu scope minim
5. **n8n MCP** — activeaza doar workflow-urile necesare pentru MCP access
6. **Sentry** — token cu read-only permissions este suficient pentru debugging
7. **NICIODATA** nu stoca API keys in `claude_desktop_config.json` pe un shared machine
8. **Rotatie keys** — roteste toate API keys la 90 de zile

---

## Verificare Post-Instalare

Dupa configurare, testeaza fiecare server cu aceste prompturi in Claude:

| Server | Test Prompt | Expected Result |
|--------|------------|-----------------|
| Stripe | "List my Stripe test products" | Lista produse test |
| PostgreSQL | "Show all tables in the database" | Lista tabele |
| GitHub | "List my recent repositories" | Lista repo-uri |
| Filesystem | "List files in the project root" | Fisiere proiect |
| Git | "Show recent commits" | Commit history |
| Sentry | "Show unresolved issues" | Lista erori |
| Puppeteer | "Take a screenshot of google.com" | Screenshot |
| Memory | "Remember that our DB uses PostgreSQL 16" | Confirmare stocare |
| n8n | "List my n8n workflows" | Lista workflows |