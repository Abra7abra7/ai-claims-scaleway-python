# 📊 AI Claims Processing - Aktuálny Stav Projektu

**Dátum aktualizácie:** 9. december 2024

---

## 🎯 Prehľad

Projekt je **production-ready** systém na spracovanie poistných udalostí pre regulované prostredie (poisťovňa) s plným audit loggingom a GDPR compliance.

---

## 🗄️ Backend

### Technológie
- **Framework:** FastAPI 0.100+
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL + pgvector
- **Queue:** Celery + Redis
- **Auth:** Custom DB sessions s PBKDF2 hashing

### API Štruktúra (`/api/v1/`)

```
/api/v1/
├── /auth/                    # Autentifikácia
│   ├── POST /register        # Registrácia
│   ├── POST /login           # Prihlásenie
│   ├── POST /logout          # Odhlásenie
│   ├── GET  /me              # Aktuálny user
│   ├── POST /password/change # Zmena hesla
│   ├── GET  /sessions        # Aktívne sessions
│   ├── POST /sessions/{id}/revoke
│   ├── POST /sessions/revoke-all
│   └── /admin/               # Admin endpoints
│
├── /health/                  # Health checks
│   ├── GET /                 # Health check
│   ├── GET /ready           # Readiness
│   └── GET /live            # Liveness
│
├── /claims/                  # Claims CRUD
│   ├── GET  /               # List claims
│   ├── POST /               # Create claim
│   ├── GET  /{id}           # Get claim detail
│   ├── DELETE /{id}         # Delete claim
│   ├── /{id}/ocr/           # OCR review
│   ├── /{id}/anon/          # Anonymization review
│   └── /{id}/analysis/      # AI Analysis
│
├── /rag/                     # RAG Management
│   ├── GET  /documents      # List RAG docs
│   ├── POST /documents      # Upload RAG doc
│   ├── DELETE /documents/{id}
│   └── POST /search         # Vector search
│
├── /reports/                 # PDF Reports
│   ├── GET  /               # List reports
│   ├── POST /               # Generate report
│   └── GET  /{id}/download  # Download PDF
│
├── /prompts/                 # Prompt Templates
│   ├── GET  /               # List prompts
│   ├── POST /               # Create prompt
│   ├── PUT  /{id}           # Update prompt
│   └── DELETE /{id}         # Delete prompt
│
├── /audit/                   # Audit Logs
│   ├── GET /                # List audit logs
│   └── GET /claim/{id}      # Claim audit trail
│
└── /stats/                   # Statistics
    └── GET /dashboard       # Dashboard stats
```

### Database Modely

```python
# Hlavné modely (app/db/models.py)

class User              # Používatelia
  - id, email, password_hash, name
  - role (admin/user/viewer)
  - locale (sk/en)
  - is_active, email_verified
  - created_at, updated_at, last_login_at

class UserSession       # Auth sessions
  - id, user_id, token
  - ip_address, user_agent
  - created_at, expires_at, last_activity_at
  - is_revoked, revoked_at, revoked_reason

class Claim             # Poistné udalosti
  - id, created_at, country
  - status (PROCESSING→ANALYZED)
  - analysis_result (JSONB)

class ClaimDocument     # Dokumenty
  - id, claim_id, filename, s3_key
  - original_text, cleaned_text, anonymized_text
  - embedding (Vector 1024)
  - ocr_reviewed_by, anon_reviewed_by

class RAGDocument       # Knowledge base
  - id, filename, s3_key
  - country, document_type
  - text_content, embedding

class AuditLog          # Audit trail
  - id, user, action, entity_type, entity_id
  - changes (JSONB), timestamp

class AnalysisReport    # PDF reporty
  - id, claim_id, s3_key, model_used, prompt_id

class PromptTemplate    # LLM prompty
  - id, name, description, template, llm_model
```

### Schemas (Pydantic)

```
app/api/v1/schemas/
├── auth.py           # UserLoginRequest, LoginResponse, SessionResponse...
├── claims.py         # ClaimCreate, ClaimResponse, ClaimListResponse...
├── documents.py      # DocumentResponse, OCRReviewRequest...
├── rag.py            # RAGDocumentCreate, RAGSearchRequest...
├── analysis.py       # AnalysisRequest, AnalysisResponse...
├── reports.py        # ReportRequest, ReportResponse...
├── audit.py          # AuditLogResponse, AuditListResponse...
├── stats.py          # DashboardStats, StatusCount...
└── prompts.py        # PromptCreate, PromptResponse...
```

### Services

```
app/services/
├── auth.py           # AuthService - login, logout, sessions
├── audit.py          # AuditLogger - všetky akcie logované
├── ocr.py            # Mistral Document OCR
├── cleaning.py       # Text cleaning rules
├── anonymization.py  # Presidio integration
├── analysis.py       # LLM analysis s RAG
├── storage.py        # S3 operations
├── rag.py            # Vector search, embeddings
└── reports.py        # PDF generation
```

---

## 🎨 Frontend

### Technológie
- **Framework:** Next.js 16
- **UI:** React 19
- **Styling:** TailwindCSS v4, shadcn/ui
- **i18n:** next-intl (SK/EN)
- **State:** React Query
- **API:** openapi-fetch (type-safe)

### Štruktúra

```
frontend/src/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard (/)
│   ├── auth/
│   │   ├── sign-in/page.tsx # Login stránka
│   │   └── sign-up/page.tsx # Registrácia
│   ├── claims/
│   │   ├── page.tsx         # Claims list
│   │   ├── new/page.tsx     # Upload new claim
│   │   └── [id]/page.tsx    # Claim detail
│   └── api/
│       └── auth/[...all]/route.ts  # Auth API route
│
├── components/
│   ├── ui/                  # shadcn komponenty
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── sidebar.tsx      # Navigácia
│   │   └── app-layout.tsx   # Main layout
│   ├── dashboard/
│   │   └── dashboard-content.tsx
│   ├── claims/
│   │   ├── claims-list.tsx
│   │   ├── claim-detail.tsx
│   │   └── claim-upload.tsx
│   └── providers/
│       └── providers.tsx    # QueryClient, Themes
│
├── lib/
│   ├── auth-client.ts       # Auth funkcie (login, logout, useSession)
│   ├── api.ts               # Type-safe API client
│   ├── api-types.ts         # Generated from OpenAPI
│   └── utils.ts             # Utility funkcie
│
├── i18n/
│   └── request.ts           # next-intl config
│
├── messages/
│   ├── sk.json              # Slovenské preklady
│   └── en.json              # Anglické preklady
│
└── middleware.ts            # i18n middleware
```

### Theme (Dark)

```css
/* Hlavné farby */
--background: oklch(0.1 0 0);      /* Tmavé pozadie */
--foreground: oklch(0.98 0 0);     /* Svetlý text */
--primary: oklch(0.55 0.2 150);    /* Zelená */
--card: oklch(0.14 0 0);           /* Card pozadie */
--border: oklch(0.25 0 0);         /* Borders */
```

### Preklady (i18n)

```json
// messages/sk.json
{
  "app": { "title": "AI Claims" },
  "nav": { "dashboard": "Dashboard", "claims": "Poistné udalosti" },
  "auth": { "signIn": "Prihlásiť sa", "signOut": "Odhlásiť sa" },
  "claims": { "title": "Poistné udalosti", "new": "Nová udalosť" },
  "dashboard": { "title": "Dashboard", "totalClaims": "Celkom udalostí" }
}
```

---

## 🔐 Autentifikácia

### Flow

```
1. User zadá email + password
2. Frontend: POST /api/v1/auth/login
3. Backend: 
   - Overí credentials
   - Vytvorí UserSession v DB
   - Nastaví HTTP-only cookie
   - Loguje do AuditLog (LOGIN_SUCCESS/FAILED)
4. Frontend: Redirect na Dashboard
5. Každý request: Cookie automaticky posielaná
6. Backend: Validuje session, aktualizuje last_activity
7. Po 7 dňoch alebo 24h nečinnosti: Session expiruje
```

### Audit Akcie

```python
# Logované akcie
LOGIN_SUCCESS      # Úspešné prihlásenie
LOGIN_FAILED       # Neúspešné prihlásenie (+ dôvod)
LOGOUT             # Odhlásenie
REGISTER_SUCCESS   # Nová registrácia
REGISTER_FAILED    # Neúspešná registrácia
PASSWORD_CHANGED   # Zmena hesla
SESSION_REVOKED    # Zrušenie session
ALL_SESSIONS_REVOKED # Odhlásenie všade
```

### Session Management

```python
# Nastavenia
SESSION_DURATION_HOURS = 168     # 7 dní
SESSION_INACTIVITY_HOURS = 24    # 24h timeout

# Čo sa loguje
- IP adresa (X-Forwarded-For podporované)
- User-Agent (browser/device)
- Timestamp vytvorenia
- Last activity
- Revocation reason (ak revokované)
```

---

## 📁 Súborová Štruktúra

```
ai-claims-scaleway-python/
├── app/                          # Backend
│   ├── api/v1/
│   │   ├── endpoints/            # API endpoints
│   │   ├── schemas/              # Pydantic schemas
│   │   └── router.py             # Main router
│   ├── core/
│   │   └── config.py             # Settings
│   ├── db/
│   │   ├── models.py             # SQLAlchemy models
│   │   └── session.py            # DB session
│   ├── services/                 # Business logic
│   ├── main.py                   # FastAPI app
│   └── worker.py                 # Celery worker
│
├── frontend/                     # Frontend
│   ├── src/
│   │   ├── app/                  # Next.js pages
│   │   ├── components/           # React components
│   │   ├── lib/                  # Utils, API client
│   │   ├── messages/             # i18n translations
│   │   └── middleware.ts
│   ├── package.json
│   └── Dockerfile
│
├── presidio-api/                 # Presidio service
│   ├── app.py
│   ├── config/
│   └── Dockerfile
│
├── deploy/                       # Deployment scripts
├── docs/                         # Dokumentácia
├── scripts/                      # Utility scripts
│
├── docker-compose.yml            # Local development
├── docker-compose.prod.yml       # Production
├── Dockerfile.backend
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🐳 Docker Services

```yaml
services:
  backend:     # FastAPI (port 8000)
  frontend:    # Next.js (port 3000)
  worker:      # Celery worker
  presidio:    # Anonymization (port 8001)
  db:          # PostgreSQL (port 5432)
  redis:       # Redis (port 6379)
  minio:       # Local S3 (port 9000)
```

---

## ✅ Aktuálny Stav (9.12.2024)

### Dokončené
- [x] Backend API (FastAPI)
- [x] Database modely (Users, Sessions, Claims, Documents, Audit)
- [x] Autentifikácia s DB sessions
- [x] Audit logging (všetky akcie)
- [x] OCR s Mistral AI
- [x] Text cleaning
- [x] Presidio anonymization (SK, IT, DE)
- [x] RAG systém (pgvector)
- [x] AI analýza (Mistral, Gemini, OpenAI)
- [x] PDF report generation
- [x] Frontend (Next.js 16)
- [x] Dark theme
- [x] Multi-language (SK/EN)
- [x] Dashboard so štatistikami
- [x] Claims management UI

### TODO
- [ ] Forgot password flow
- [ ] Email verification
- [ ] Google OAuth (pripravené, potrebuje credentials)
- [ ] User management UI (admin panel)
- [ ] Session management UI (logged devices)
- [ ] Full test coverage
- [ ] Production deployment update

---

## 🚀 Quick Commands

```bash
# Spustiť všetko
docker compose up -d

# Pozrieť logy
docker compose logs -f backend
docker compose logs -f frontend

# Reštart služby
docker compose restart backend

# Rebuild frontend
docker compose build frontend --no-cache
docker compose up -d frontend

# Vytvoriť admin usera
docker compose exec backend python -c "
from app.db.session import SessionLocal
from app.db.models import User
from app.services.auth import hash_password
db = SessionLocal()
admin = User(email='admin@example.com', password_hash=hash_password('admin123456'), name='Admin', role='admin', is_active=True, email_verified=True, locale='sk')
db.add(admin)
db.commit()
db.close()
"

# Test login
docker compose exec backend python -c "
import requests
r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email': 'admin@example.com', 'password': 'admin123456'})
print(r.json())
"
```

---

## 📞 Kontakt

Pre otázky otvorte issue na GitHub alebo kontaktujte vývojový tím.

---

*Dokument vytvorený: 9. december 2024*

