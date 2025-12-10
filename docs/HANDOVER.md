# 🤖 AI Claims Processing System - Handover Dokumentácia

**Dátum odovzdania:** 9. december 2024  
**Verzia:** 1.0  
**Status:** Production-ready

---

## 📋 Obsah

1. [Úvod a Kontext](#úvod-a-kontext)
2. [História Vývoja](#história-vývoja)
3. [Architektúra Systému](#architektúra-systému)
4. [Bezpečnosť](#bezpečnosť)
5. [Workflow Spracovania](#workflow-spracovania)
6. [Lokálny Vývoj](#lokálny-vývoj)
7. [Production Deployment](#production-deployment)
8. [Správa Systému](#správa-systému)
9. [Riešenie Problémov](#riešenie-problémov)
10. [Budúci Vývoj](#budúci-vývoj)

---

## 🎯 Úvod a Kontext

### Čo je AI Claims?

**AI Claims Processing System** je prvý AI asistent pre spracovanie poistných udalostí v súlade s EU právom. Systém automatizuje proces spracovania PDF dokumentov od OCR extrakcie až po AI analýzu s plnou GDPR compliance.

### Prečo vznikol?

Systém vznikol pre regulované prostredie poisťovne, kde je potrebné:
- ✅ Automatizované spracovanie poistných udalostí
- ✅ GDPR anonymizácia osobných údajov
- ✅ Human-in-the-loop kontrolné body
- ✅ Kompletný audit trail všetkých akcií
- ✅ Bezpečná autentifikácia a session management

### Pre koho je určený?

- **Claims handlers** - spracovanie poistných udalostí
- **Compliance officers** - audit log monitoring
- **IT admins** - správa používateľov a systému

---

## 📊 História Vývoja

### Timeline

| Dátum | Udalosť |
|-------|---------|
| **19. november 2024** | Začiatok vývoja, prvý commit |
| **Týždeň 1-2** | Základná architektúra (FastAPI + Next.js) |
| **Týždeň 2** | Scaleway integrácia → pivot na lokálny vývoj |
| **Týždeň 3** | Enterprise autentifikácia + email flows |
| **9. december 2024** | Production deployment, handover |

### Vývoj v číslach

- **Trvanie:** 3 týždne (19. nov - 9. dec 2024)
- **Počet commitov:** 32
- **Hlavné features:** 12
- **API endpoints:** 40+
- **Frontend stránky:** 15+

### História Hostingu

#### Fáza 1: Scaleway (november 2024)
- **Plán:** Cloud hosting na Scaleway
  - Managed PostgreSQL database
  - S3 Object Storage
  - Európske dátové centrá (GDPR)
- **Problém:** Scaleway začal účtovať poplatky okamžite
- **Rozhodnutie:** Pivot na lokálny vývoj

#### Fáza 2: Lokálny vývoj (november 2024)
- MinIO namiesto Scaleway S3 (S3-compatible)
- Lokálny PostgreSQL v Docker kontajneri
- Kompletný stack v Docker Compose
- Možnosť prepnúť späť na Scaleway v budúcnosti

#### Fáza 3: IBM Server v Novis (december 2024) - AKTUÁLNE
- **Server:** 10.85.55.26 (IBM infraštruktúra)
- **URL:** https://ai-claims.novis.eu
- **Deployment:** Docker Compose
- **Storage:** MinIO (možnosť upgrade na Scaleway)
- **Database:** PostgreSQL + pgvector
- **SSL:** Certifikát pre ai-claims.novis.eu

---

## 🏗️ Architektúra Systému

### Prehľad Komponentov

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 16)                        │
│                      Port: 3000                                 │
│  - React 19, shadcn/ui, next-intl (SK/EN)                      │
│  - Type-safe API calls (auto-generated types)                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ HTTPS/REST API
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                      Port: 8000                                 │
│  - SQLAlchemy ORM, Pydantic validation                         │
│  - OpenAPI/Swagger docs                                         │
│  - JWT sessions with audit logging                              │
└─────┬──────────────────┬─────────────────┬──────────────────────┘
      │                  │                 │
      ↓                  ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │   Presidio   │
│  + pgvector  │  │    :6379     │  │   API :8001  │
│   :5432      │  │              │  │              │
│              │  │  - Queue     │  │  - PII       │
│  - Users     │  │  - Cache     │  │  Detection   │
│  - Claims    │  └──────┬───────┘  └──────────────┘
│  - Sessions  │         │
│  - Audit Log │         ↓
│  - Tokens    │  ┌──────────────┐
└──────┬───────┘  │    Worker    │
       │          │   (Celery)   │
       │          │              │
       │          │  - OCR tasks │
       │          │  - Analysis  │
       │          └──────────────┘
       ↓
┌──────────────────────────────────┐
│        MinIO / S3 Storage        │
│            :9000-9001            │
│                                  │
│  - PDF dokumenty                 │
│  - Extracted text                │
│  - Generated reports             │
│  - RAG policy documents          │
└──────────────────────────────────┘
```

### Tech Stack

#### Frontend
- **Framework:** Next.js 16 (React 19)
- **UI Library:** shadcn/ui (Tailwind CSS)
- **Internationalization:** next-intl (SK, EN)
- **State Management:** React Query (TanStack Query)
- **Type Safety:** TypeScript 5, auto-generated types z OpenAPI
- **Forms:** react-hook-form + Zod validation

#### Backend
- **Framework:** FastAPI 0.100+
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic v2
- **API Docs:** OpenAPI 3.1 (Swagger UI, ReDoc)
- **Authentication:** Custom DB sessions (PBKDF2-SHA256)
- **Queue:** Celery + Redis
- **Storage:** S3-compatible (MinIO/Scaleway)

#### Database
- **Engine:** PostgreSQL 16
- **Extension:** pgvector (vector embeddings)
- **Tables:** 8 hlavných tabuliek (users, claims, documents, sessions, audit_logs, tokens, rag_documents, prompts)

#### AI & Services
- **OCR:** Mistral AI Document OCR
- **PII Detection:** Microsoft Presidio (country-specific: SK, IT, DE)
- **LLM Providers:** Mistral AI, Google Gemini, OpenAI (configurable)
- **RAG:** Vector search cez pgvector

#### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** (konfigurovať podľa potreby)
- **SSL:** Let's Encrypt / vlastný certifikát
- **Monitoring:** Docker logs, audit_logs tabuľka

---

## 🔐 Bezpečnosť

### Autentifikácia

#### Prečo vlastný auth namiesto Better Auth?
- **Regulované prostredie** - potreba plnej kontroly
- **Audit logging** - každá akcia musí byť zalogovaná
- **Session management** - IP address + User-Agent tracking
- **GDPR compliance** - plná kontrola nad user data

#### Ako funguje?

1. **Registrácia:**
   - User vyplní formulár
   - Backend vytvorí účet (`email_verified = FALSE`)
   - Automaticky pošle verification email (platný 24h)
   - Presmerovanie na sign-in page

2. **Email Verification:**
   - User klikne link v emaile
   - Token sa overí (jednorázový, expiruje)
   - `email_verified = TRUE`
   - Audit log: `EMAIL_VERIFIED`

3. **Login:**
   - User zadá email + heslo
   - Backend overí credentials
   - **Kontrola:** `email_verified` musí byť TRUE
   - Vytvorí DB session (nie JWT token!)
   - HTTP-only cookie s session ID
   - Audit log: `LOGIN_SUCCESS` + IP + User-Agent

4. **Session Management:**
   - Session uložená v PostgreSQL
   - Platnosť: 7 dní
   - Možnosť revokovať jednotlivé sessions
   - "Logout everywhere" revokuje všetky sessions

5. **Password Reset:**
   - User klikne "Forgot password?"
   - Backend pošle reset email (platný 1h)
   - User klikne link → nastav nové heslo
   - **Auto-verify email** (dokázal vlastníctvo)
   - Všetky sessions zrušené (force re-login)

### Bezpečnostné Vlastnosti

- ✅ **PBKDF2-SHA256** password hashing (100,000 iterácií)
- ✅ **HTTP-only cookies** (nie localStorage)
- ✅ **Session tokens** uložené v DB (možnosť okamžitého revoke)
- ✅ **Email verification** povinná
- ✅ **IP address logging** pre všetky login pokusy
- ✅ **User-Agent tracking** pre detekciu suspicious sessions
- ✅ **Audit trail** každej akcie (GDPR compliance)
- ✅ **CORS** konfigurovaný pre production domain
- ✅ **Rate limiting** (možnosť pridať)

### Role-Based Access Control

- **USER** - základné oprávnenia (view claims, upload documents)
- **ADMIN** - plné oprávnenia (user management, audit logs, system stats)

### GDPR Compliance

1. **PII Anonymizácia** - Microsoft Presidio (country-specific)
2. **Audit Logging** - každá akcia zalogovaná
3. **Right to be forgotten** - možnosť vymazať user data
4. **Data minimization** - len potrebné údaje
5. **Secure sessions** - DB-based, revocable

---

## 🔄 Workflow Spracovania Poistnej Udalosti

### Krok po kroku

```
1. 📤 UPLOAD
   User: Nahrá PDF dokument
   Systém: Uloží do MinIO/S3, vytvorí claim
   Status: UPLOADED

2. 🔍 OCR EXTRACTION
   Worker: Mistral AI Document OCR
   Systém: Extrahuje text z PDF
   Status: OCR_PROCESSING → OCR_COMPLETED

3. 🧹 DATA CLEANING
   Worker: Pravidlové čistenie OCR šumu
   Systém: Odstráni artefakty, normalizuje text
   Status: CLEANING

4. 👁️ HUMAN REVIEW #1 - OCR
   User: Skontroluje a upraví extrahovaný text
   Akcia: /claims/{id}/ocr (approve/reject)
   Status: OCR_REVIEW_NEEDED → OCR_APPROVED

5. 🔒 ANONYMIZÁCIA
   Worker: Presidio anonymizácia (SK/IT/DE)
   Systém: Detekuje a maskuje PII (mená, adresy, atď.)
   Status: ANONYMIZATION_PROCESSING

6. 👁️ HUMAN REVIEW #2 - ANONYMIZÁCIA
   User: Skontroluje side-by-side (cleaned vs anonymized)
   Akcia: /claims/{id}/anon (approve/reject)
   Status: ANON_REVIEW_NEEDED → ANON_APPROVED

7. 🤖 AI ANALÝZA
   User: Vyberie prompt, spustí analýzu
   Worker: RAG-enhanced AI analýza s policy documents
   Systém: Generuje structured response
   Status: ANALYSIS_STARTED → ANALYSIS_COMPLETED

8. 📄 PDF REPORT
   Systém: Automaticky generuje PDF report
   User: Stiahne report cez /reports
   Status: COMPLETED

9. 📊 AUDIT LOG
   Systém: Každý krok zalogovaný
   Admin: Môže zobraziť kompletný audit trail
```

### Stavy Claimu

| Status | Popis | Ďalší krok |
|--------|-------|------------|
| `UPLOADED` | Dokument nahraný | OCR spracovanie |
| `OCR_PROCESSING` | OCR prebieha | Čaká na dokončenie |
| `OCR_COMPLETED` | OCR hotové | Human review |
| `OCR_REVIEW_NEEDED` | Čaká na kontrolu | User approves |
| `OCR_APPROVED` | OCR schválené | Anonymizácia |
| `ANONYMIZATION_PROCESSING` | Anonymizácia prebieha | Čaká na dokončenie |
| `ANON_REVIEW_NEEDED` | Čaká na anon kontrolu | User approves |
| `ANON_APPROVED` | Anon schválené | AI analýza |
| `ANALYSIS_STARTED` | Analýza prebieha | Čaká na dokončenie |
| `ANALYSIS_COMPLETED` | Analýza hotová | Report ready |
| `COMPLETED` | Všetko hotové | Archivované |
| `FAILED` | Chyba v procese | Manual retry |

---

## 🏗️ Architektúra Systému

### Docker Services

#### 1. **Frontend** (Next.js)
- **Port:** 3000
- **Technológie:** Next.js 16, React 19, Turbopack
- **Úloha:** Používateľské rozhranie
- **Volumes:** `./frontend:/app` (hot reload)
- **Environment:** `NEXT_PUBLIC_API_URL`

#### 2. **Backend** (FastAPI)
- **Port:** 8000
- **Technológie:** FastAPI, SQLAlchemy, Pydantic
- **Úloha:** REST API, business logic
- **Volumes:** `./app:/app/app` (hot reload)
- **Environment:** DATABASE_URL, MISTRAL_API_KEY, SMTP_*, atď.

#### 3. **Worker** (Celery)
- **Technológie:** Celery, same ako backend
- **Úloha:** Background tasks (OCR, anonymizácia, analýza)
- **Queue:** Redis
- **Environment:** Same ako backend

#### 4. **Database** (PostgreSQL + pgvector)
- **Port:** 5432
- **Image:** pgvector/pgvector:pg16
- **Úloha:** Persistent storage, vector embeddings
- **Volume:** `postgres_data`
- **Health check:** `pg_isready`

#### 5. **Redis**
- **Port:** 6379
- **Image:** redis:7-alpine
- **Úloha:** Celery queue, cache
- **Lightweight:** Memory-based

#### 6. **MinIO** (S3-compatible)
- **Ports:** 9000 (API), 9001 (Console)
- **Image:** minio/minio:latest
- **Úloha:** Object storage (PDF, reports)
- **Volume:** `minio_data`
- **Alternative:** Možnosť prepnúť na Scaleway S3

#### 7. **Presidio API**
- **Port:** 8001
- **Technológie:** Microsoft Presidio
- **Úloha:** PII detection & anonymization
- **Podporované krajiny:** SK, IT, DE
- **Health check:** `/health`

### Data Flow

```
User Upload PDF
      ↓
Frontend → Backend API → MinIO (uloží PDF)
      ↓
Backend → Celery Queue (OCR task)
      ↓
Worker → Mistral AI OCR → extracts text
      ↓
Worker → saves to PostgreSQL → Status: OCR_COMPLETED
      ↓
User reviews OCR → approves
      ↓
Backend → Celery Queue (Anonymization task)
      ↓
Worker → Presidio API → detects PII → anonymizes
      ↓
User reviews Anon → approves
      ↓
Backend → Celery Queue (Analysis task)
      ↓
Worker → RAG (pgvector) + LLM → generates analysis
      ↓
Backend → generates PDF report → saves to MinIO
      ↓
User downloads report
```

### API Endpoints

Kompletný zoznam je v `docs/ARCHITECTURE.md`, hlavné sekcie:

- **`/api/v1/auth/*`** - Autentifikácia (12 endpoints)
- **`/api/v1/claims/*`** - Claims CRUD (8 endpoints)
- **`/api/v1/ocr/*`** - OCR review (3 endpoints)
- **`/api/v1/anonymization/*`** - Anonymization review (3 endpoints)
- **`/api/v1/analysis/*`** - AI analýza (4 endpoints)
- **`/api/v1/rag/*`** - Policy documents (6 endpoints)
- **`/api/v1/reports/*`** - Report management (3 endpoints)
- **`/api/v1/audit/*`** - Audit logs (2 endpoints)
- **`/api/v1/stats/*`** - Štatistiky (3 endpoints)
- **`/api/v1/health/*`** - Health checks (3 endpoints)

**Celkom:** 40+ REST API endpoints

### Frontend Štruktúra

```
frontend/src/
├── app/                        # Next.js App Router
│   ├── page.tsx               # Dashboard (stats)
│   ├── auth/                  # Autentifikácia
│   │   ├── sign-in/          # Prihlásenie
│   │   ├── sign-up/          # Registrácia
│   │   ├── forgot-password/  # Zabudnuté heslo
│   │   ├── reset-password/   # Reset hesla (email link)
│   │   └── verify-email/     # Email verifikácia (email link)
│   ├── claims/               # Claims management
│   │   ├── page.tsx          # Zoznam claims
│   │   ├── new/              # Nový claim
│   │   └── [id]/             # Detail claimu
│   │       ├── page.tsx      # Prehľad
│   │       ├── ocr/          # OCR review
│   │       ├── anon/         # Anonymizácia review
│   │       └── analysis/     # AI analýza
│   ├── rag/                  # RAG documents
│   ├── reports/              # Report management
│   ├── audit/                # Audit log (admin)
│   ├── settings/             # User settings
│   │   ├── page.tsx          # Profil, zmena hesla
│   │   └── sessions/         # Session management
│   └── admin/                # Admin sekcia
│       └── users/            # User management
│
├── components/               # React komponenty
│   ├── ui/                   # shadcn/ui komponenty
│   ├── layout/               # Layout (sidebar, app-layout)
│   ├── claims/               # Claims-specific komponenty
│   └── dashboard/            # Dashboard komponenty
│
├── lib/                      # Utilities
│   ├── api-types.ts          # Auto-generované typy (OpenAPI)
│   ├── types.ts              # Helper type exports
│   ├── api.ts                # Type-safe API client
│   ├── auth-client.ts        # Auth utilities
│   └── utils.ts              # Misc utilities
│
└── messages/                 # Translations
    ├── sk.json               # Slovenčina
    └── en.json               # English
```

---

## 🔐 Bezpečnosť

### Autentifikácia a Autorizácia

#### Session Management
- **Storage:** PostgreSQL (nie JWT v localStorage)
- **Token:** Náhodný bezpečný string (32+ bytes)
- **Delivery:** HTTP-only cookie
- **Expiration:** 7 dní
- **Revocation:** Okamžitá (DB delete)
- **Tracking:** IP address + User-Agent

#### Password Security
- **Algorithm:** PBKDF2-SHA256
- **Iterations:** 100,000
- **Salt:** Unique per user (32 bytes)
- **Min length:** 8 znakov
- **Validation:** Server-side (Pydantic)

#### Email Verification
- **Povinná:** Áno (pred prvým login)
- **Token:** Jednorázový, 24h platnosť
- **Flow:** Register → Email → Verify → Login
- **Bypass:** Password reset auto-verifikuje email

#### Password Reset
- **Token:** Jednorázový, 1h platnosť
- **Security:** Email ownership proof
- **Side effect:** Auto-verify email, revoke všetky sessions
- **Audit:** Zalogované s IP address

### Audit Logging

Každá akcia je zalogovaná v `audit_logs` tabuľke:

#### Akcie ktoré sa logujú:
- `REGISTER_SUCCESS` / `REGISTER_FAILED`
- `LOGIN_SUCCESS` / `LOGIN_FAILED`
- `LOGOUT`
- `EMAIL_VERIFIED`
- `PASSWORD_CHANGED`
- `PASSWORD_RESET_REQUESTED` / `PASSWORD_RESET_COMPLETED`
- `SESSION_REVOKED` / `ALL_SESSIONS_REVOKED`
- `CLAIM_CREATED` / `CLAIM_UPDATED` / `CLAIM_DELETED`
- `OCR_APPROVED` / `OCR_REJECTED`
- `ANON_APPROVED` / `ANON_REJECTED`
- `ANALYSIS_STARTED` / `ANALYSIS_COMPLETED`
- ... a všetky ostatné akcie

#### Audit Log obsahuje:
- Timestamp (UTC)
- User email
- Action type
- Entity type + ID
- Changes (JSON)
- IP address
- User-Agent
- Success/failure

### CORS Konfigurácia

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-claims.novis.eu",  # Production
        "http://localhost:3000"         # Development
    ],
    allow_credentials=True,  # Pre cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables Security

**NIKDY necommitovať `.env` do Git!**

Prečo?
- Obsahuje API keys (Mistral - GDPR compliant)
- SMTP password
- Database credentials
- S3 secrets

`.gitignore` už obsahuje `.env`, ale vždy skontroluj pred commitom:
```bash
git status  # Skontroluj že .env NIE JE staged
```

---

## 🚀 Lokálny Vývoj

### Prvotné Nastavenie

#### 1. Klonovať repository
```bash
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python
```

#### 2. Nakonfigurovať .env

Vytvor `.env` súbor v root directory:

```bash
# Database
DATABASE_URL=postgresql://claims_user:claims_password@db:5432/claims_db

# AI Providers (Mistral recommended - GDPR compliant)
MISTRAL_API_KEY=your-mistral-api-key
LLM_PROVIDER=mistral

# Alternative providers (optional)
# GEMINI_API_KEY=your-gemini-api-key

# MinIO (lokálny vývoj)
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=ai-claims
S3_ENDPOINT_URL=http://minio:9000
S3_REGION=us-east-1

# Email (SMTP) - POVINNÉ!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tvoj-email@gmail.com
SMTP_PASSWORD=tvoj-app-password  # Gmail App Password!
SMTP_FROM=noreply@novis.eu
SMTP_USE_TLS=true
FRONTEND_URL=http://localhost:3000
```

**Ako získať Gmail App Password:**
1. Choď na https://myaccount.google.com/apppasswords
2. Vytvor nový "Mail" app password
3. Skopíruj 16-znakový kód
4. Vlož do `.env` (bez medzier)

#### 3. Spustiť Docker služby
```bash
docker-compose up -d
```

Počkaj 30-60 sekúnd kým všetky služby naštartujú.

#### 4. Vytvoriť admin používateľa
```bash
docker-compose exec backend python scripts/init_admin.py
```

Výstup:
```
Admin user created:
Email: admin@example.com
Password: admin123
```

#### 5. Otvoriť aplikáciu
```
http://localhost:3000
```

Prihlás sa s admin credentials.

### Denný Development Workflow

#### Zmeny v Backende
```bash
# 1. Uprav súbor v app/
# 2. Backend sa auto-reload (--reload flag)
# 3. Swagger docs aktualizované: http://localhost:8000/api/v1/docs
```

#### Zmeny vo Frontende
```bash
# 1. Uprav súbor v frontend/src/
# 2. Next.js auto-reload (Fast Refresh)
# 3. Vidíš zmeny okamžite
```

#### Zmeny v API (pridanie endpointu)
```bash
# 1. Pridaj endpoint do app/api/v1/endpoints/*.py
# 2. Pridaj schema do app/api/v1/schemas/*.py
# 3. Registruj v app/api/v1/router.py
# 4. Vygeneruj TypeScript typy:
cd frontend
npm run generate-types
# 5. Typy sa auto-vygenerujú aj pri git commit (pre-commit hook)
```

### Prístup k Službám (Development & Production)

#### 🗄️ Database (PostgreSQL)

**Lokálne:**
```bash
# Priamy prístup cez psql
docker-compose exec db psql -U claims_user -d claims_db

# SQL queries
SELECT * FROM users;
SELECT * FROM claims ORDER BY created_at DESC LIMIT 10;
SELECT * FROM audit_logs WHERE action LIKE 'LOGIN%';

# Backup databázy
docker-compose exec db pg_dump -U claims_user claims_db > backup_$(date +%Y%m%d).sql
```

**Produkcia (IBM Server):**
```bash
# SSH do servera
ssh user@10.85.55.26

# Pripojenie k DB
docker-compose exec db psql -U claims_user -d claims_db
```

**Connection String:**
```
postgresql://claims_user:claims_password@localhost:5432/claims_db  # Lokálne
postgresql://claims_user:claims_password@10.85.55.26:5432/claims_db  # Production (ak exposed)
```

#### 📦 Storage (MinIO / S3)

**MinIO Console (Lokálne):**
- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin123`
- Bucket: `ai-claims`

**Produkcia:**
- MinIO Console: http://10.85.55.26:9001 (ak exposed)
- Alebo cez `docker-compose exec` príkazy

**Štruktúra dokumentov v buckete:**
```
ai-claims/
├── claims/{claim_id}/
│   ├── original/       # Nahraté PDF
│   ├── processed/      # Po OCR/cleaning
│   └── reports/        # Vygenerované reporty
└── rag/
    └── {country}/{type}/  # Policy dokumenty (SK/general/, SK/health/, atď.)
```

#### 📖 API Dokumentácia (Swagger / OpenAPI)

**Lokálne:**
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

**Produkcia:**
- **URL:** https://ai-claims.novis.eu/api/v1/docs
- **Poznámka:** ⚠️ Ak dostávaš "Bad Gateway" na produkcii, skontroluj:
  1. Backend beží: `docker-compose ps backend`
  2. Backend loguje správne: `docker-compose logs backend`
  3. Reverse proxy (nginx/traefik) je nakonfigurovaný pre `/api/v1/*` routes
  4. CORS povoľuje `https://ai-claims.novis.eu`

**Typová generácia z API:**
```bash
# Lokálne
cd frontend
npm run generate-types

# Z production API
npx openapi-typescript https://ai-claims.novis.eu/api/v1/openapi.json -o src/lib/api-types.ts
```

### Užitočné Príkazy

```bash
# Zobraziť logy
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Reštartovať službu
docker-compose restart backend
docker-compose restart frontend

# Vymazať všetko a začať odznova
docker-compose down -v  # POZOR: Vymaže DB data!
docker-compose up -d

# Vstúpiť do kontajnera
docker-compose exec backend bash
docker-compose exec db psql -U claims_user -d claims_db

# Overiť status služieb
docker-compose ps

# Zobraziť environment variables
docker-compose config | grep SMTP
```

---

## 🌐 Production Deployment

### Aktuálny Server (IBM v Novis)

- **IP:** 10.85.55.26
- **Hostname:** ai-claims.novis.eu
- **OS:** Linux (Docker nainštalovaný)
- **Deployment:** Docker Compose
- **SSL:** Certifikát pre https://ai-claims.novis.eu

### Deployment Proces

Detailný návod je v `docs/PRODUCTION_DEPLOYMENT.md`.

#### Rýchly Postup

```bash
# 1. SSH pripojenie
ssh user@10.85.55.26

# 2. Pull najnovšie zmeny
cd /path/to/ai-claims-scaleway-python
git pull

# 3. Nakonfigurovať production .env
# Upraviť SMTP, API keys, FRONTEND_URL

# 4. Spustiť s production overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 5. Overiť
docker-compose ps
curl https://ai-claims.novis.eu/api/v1/health
```

### Production Konfigurácia

#### docker-compose.prod.yml
- `FRONTEND_URL=https://ai-claims.novis.eu`
- `NEXT_PUBLIC_API_URL=https://ai-claims.novis.eu`
- `ENVIRONMENT=production`
- Resource limits (CPU, memory)
- Restart policies

#### CORS
Backend povoľuje:
- `https://ai-claims.novis.eu`
- `http://localhost:3000` (pre dev)

#### SSL/HTTPS
- Certifikát pre ai-claims.novis.eu
- Reverse proxy (nginx/traefik) pre HTTPS termination
- Redirect HTTP → HTTPS

---

## 🛠️ Správa Systému

### Správa Používateľov

#### Vytvoriť prvého admin usera
```bash
docker-compose exec backend python scripts/init_admin.py
```

#### Vytvoriť ďalších userov
- **Cez frontend:** https://ai-claims.novis.eu/auth/sign-up
- **Cez API:** POST `/api/v1/auth/register`
- **Admin panel:** `/admin/users` (enable/disable users)

#### Priama práca s užívateľmi v databáze

**Zobraziť všetkých userov:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
SELECT id, email, name, role, is_active, email_verified, created_at 
FROM users 
ORDER BY created_at DESC;
"
```

**Zmeniť rolu usera na ADMIN:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
"
```

**Manuálne verifikovať email:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
UPDATE users SET email_verified = TRUE WHERE email = 'user@example.com';
"
```

**Disablovať účet:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
UPDATE users SET is_active = FALSE WHERE email = 'user@example.com';
"
```

**Zobraziť aktívne sessions usera:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
SELECT s.id, s.ip_address, s.user_agent, s.created_at, s.last_activity_at
FROM user_sessions s
JOIN users u ON s.user_id = u.id
WHERE u.email = 'user@example.com' AND s.is_revoked = FALSE;
"
```

#### Reset hesla pre usera
1. User klikne "Forgot password?"
2. Zadá email
3. Dostane reset link (platný 1h)
4. Nastaví nové heslo
5. Auto-verifikuje email

#### Revokovať sessions
- **User:** Settings → Sessions → Revoke
- **Admin:** Admin → Users → View sessions → Revoke
- **Databázou:** `UPDATE user_sessions SET is_revoked = TRUE WHERE user_id = X;`

### Database Migrácie

#### Vytvoriť auth_tokens tabuľku (jednorazovo)
```bash
docker-compose exec db psql -U claims_user -d claims_db -c "
CREATE TABLE IF NOT EXISTS auth_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR NOT NULL UNIQUE,
    token_type VARCHAR NOT NULL,
    user_email VARCHAR NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_user_email ON auth_tokens(user_email);
"
```

#### General migrácie
```bash
docker-compose exec backend python scripts/migrate_db.py
```

### Zálohovanie

#### Database backup
```bash
# Export
docker-compose exec db pg_dump -U claims_user claims_db > backup_$(date +%Y%m%d).sql

# Import
cat backup_20241209.sql | docker-compose exec -T db psql -U claims_user -d claims_db
```

#### MinIO backup
```bash
# Export bucket
docker-compose exec minio mc mirror /data/ai-claims /backup/ai-claims

# Alebo sync na Scaleway/S3
mc mirror myminio/ai-claims scaleway/ai-claims-backup
```

### Monitoring

#### Health Checks
```bash
# Backend
curl http://localhost:8000/api/v1/health

# Presidio
curl http://localhost:8001/health

# MinIO
curl http://localhost:9000/minio/health/live
```

#### Logs
```bash
# Real-time logs
docker-compose logs -f

# Posledných 100 riadkov
docker-compose logs --tail 100 backend

# Filtrovať errors
docker-compose logs backend | grep ERROR
```

#### Audit Log
- **Frontend:** `/audit` (admin only)
- **Database query:**
```sql
SELECT * FROM audit_logs 
WHERE user = 'admin@example.com' 
ORDER BY timestamp DESC 
LIMIT 100;
```

---

## 🔧 Riešenie Problémov

### Email sa neposiela

**Symptom:** "SMTP credentials not configured" v logoch

**Riešenie:**
1. Skontroluj `.env` - sú SMTP_* premenné?
2. Skontroluj `docker-compose.yml` - sú ENV premenné v backend service?
3. Reštartuj: `docker-compose down backend && docker-compose up -d backend`
4. Overil: `docker-compose exec backend python -c "from app.core.config import get_settings; s = get_settings(); print(s.SMTP_USER)"`

### TypeScript typy nie sú aktuálne

**Symptom:** Type errors vo frontende po zmene backend API

**Riešenie:**
```bash
cd frontend
npm run generate-types
```

Alebo počkaj na git commit - pre-commit hook ich vygeneruje automaticky.

### Frontend 404 po pridaní novej stránky

**Symptom:** Nová stránka vracia 404

**Riešenie:**
```bash
docker-compose restart frontend
```

Next.js potrebuje reload pre nové routes.

### Backend nenačítava .env zmeny

**Symptom:** ENV premenné sú v `.env` ale backend ich nevidí

**Riešenie:**
```bash
# docker-compose restart nečíta nové ENV!
# Treba down + up:
docker-compose down backend
docker-compose up -d backend
```

### Database connection errors

**Symptom:** "Connection refused" alebo "database does not exist"

**Riešenie:**
```bash
# Skontroluj health
docker-compose ps

# Restartuj DB
docker-compose restart db

# Vymaž a znova vytvor (POZOR: data loss!)
docker-compose down db
docker volume rm ai-claims-scaleway-python_postgres_data
docker-compose up -d db
```

### Worker tasks zlyhávajú

**Symptom:** Claims ostávajú v `*_PROCESSING` stave

**Riešenie:**
```bash
# Skontroluj worker logy
docker-compose logs worker

# Reštartuj worker
docker-compose restart worker

# Skontroluj Redis
docker-compose exec redis redis-cli ping
```

---

## 📚 Dôležité Súbory

### Konfigurácia

| Súbor | Účel |
|-------|------|
| `.env` | Environment variables (SECRETS!) |
| `docker-compose.yml` | Lokálny development |
| `docker-compose.prod.yml` | Production overrides |
| `app/core/config.py` | Settings trieda (Pydantic) |
| `frontend/next.config.ts` | Next.js konfigurácia |

### Scripts

| Script | Účel |
|--------|------|
| `scripts/init_admin.py` | Vytvoriť admin usera |
| `scripts/migrate_db.py` | Database migrácie |
| `scripts/create_auth_tokens_table.py` | Vytvoriť tokens tabuľku |
| `scripts/pre-commit-types.js` | Git hook pre type generation |

### Dokumentácia

| Dokument | Obsah |
|----------|-------|
| `docs/HANDOVER.md` | Tento dokument |
| `docs/ARCHITECTURE.md` | Technické detaily |
| `docs/DEVELOPMENT.md` | Development guidelines |
| `docs/PRODUCTION_DEPLOYMENT.md` | Deployment návod |
| `docs/GIT_HOOKS.md` | Automatizácia s Git hooks |
| `README.md` | Rýchly prehľad |

---

## 🔄 Časté Úlohy

### Pridať nového používateľa
```bash
# Varianta 1: Cez frontend
https://ai-claims.novis.eu/auth/sign-up

# Varianta 2: Cez API (curl/Postman)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass1234","name":"John Doe","locale":"sk"}'
```

### Zmeniť heslo
```bash
# Varianta 1: Cez frontend
Settings → Change Password

# Varianta 2: Cez API
curl -X POST http://localhost:8000/api/v1/auth/password/change \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=YOUR_TOKEN" \
  -d '{"old_password":"old123","new_password":"new12345"}'
```

### Zobraziť audit log
```bash
# Frontend (admin only)
https://ai-claims.novis.eu/audit

# Database query
docker-compose exec db psql -U claims_user -d claims_db -c \
  "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 20;"
```

### Upload RAG policy dokumentu
```bash
# Frontend
https://ai-claims.novis.eu/rag → Upload Document

# Podporované krajiny: SK, IT, DE
# Podporované typy: general, health, vehicle, property, liability
```

### Vygenerovať TypeScript typy
```bash
# Po zmene backend API
cd frontend
npm run generate-types

# Watch mode (auto-regenerate)
npm run types:watch
```

### Retry zlyhané tasky
```bash
# Manual retry cez frontend
Claims → Detail → Retry Failed Step

# Alebo delete a re-upload claim
```

---

## 🔮 Budúci Vývoj

### Plánované Features

#### Priorita 1 (Security)
- [ ] Two-Factor Authentication (TOTP)
- [ ] OAuth providers (Google, Microsoft)
- [ ] API rate limiting
- [ ] Advanced session security (device fingerprinting)

#### Priorita 2 (Features)
- [ ] Batch upload (multiple PDFs)
- [ ] Export reports (Excel, JSON)
- [ ] Advanced analytics dashboard
- [ ] Custom prompt templates (user-defined)
- [ ] Document versioning

#### Priorita 3 (Infrastructure)
- [ ] Prepnúť na Scaleway (ak budget dovolí)
- [ ] Automated DB backups
- [ ] Performance monitoring (Grafana, Prometheus)
- [ ] Load balancing (ak traffic vzrastie)

### Technický Dlh

- Pridať unit tests (pytest)
- Pridať integration tests
- CI/CD pipeline (GitHub Actions)
- Code coverage monitoring
- Dependency updates automation

### Možné Optimalizácie

- Caching pre RAG documents (Redis)
- Connection pooling optimization
- Frontend bundle size reduction
- Database indexing improvements
- Worker parallelization

---

## 📞 Kontakty a Zdroje

### Repository
- **GitHub:** https://github.com/Abra7abra7/ai-claims-scaleway-python
- **Dokumentácia:** `docs/` priečinok

### Prístupy

#### Lokálny vývoj
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/v1/docs
- **MinIO Console:** http://localhost:9001 (minioadmin/minioadmin123)

#### Production
- **Frontend:** https://ai-claims.novis.eu
- **Backend API:** https://ai-claims.novis.eu/api/v1/docs
- **Server SSH:** ssh user@10.85.55.26

#### Admin Account
```
Email: admin@example.com
Password: admin123
```
(Zmeniť po prvom prihlásení!)

### Podpora

Pre technické otázky:
1. Skontroluj `docs/` dokumentáciu
2. Pozri Swagger docs: `/api/v1/docs`
3. Audit logs: `/audit` (admin)
4. Backend logs: `docker-compose logs backend`

---

## 📝 Záver

Tento systém je **production-ready** a pripravený na prevádzku v regulovanom prostredí poisťovne.

### Kľúčové Vlastnosti
- ✅ Enterprise-grade autentifikácia
- ✅ GDPR compliance (anonymizácia + audit)
- ✅ Email verification & password reset
- ✅ Multi-language (SK/EN)
- ✅ Type-safe frontend (TypeScript)
- ✅ Kompletná API dokumentácia (OpenAPI)
- ✅ Docker-based deployment
- ✅ Human-in-the-loop review points

### Odporúčania Pre Kolegov

1. **Prečítaj si `docs/ARCHITECTURE.md`** pre technické detaily
2. **Spusti lokálne** a otestuj všetky features
3. **Skontroluj audit logs** aby si videl čo sa loguje
4. **Vytvor testovacích userov** a prejdi celý workflow
5. **Prečítaj `docs/DEVELOPMENT.md`** pred úpravami kódu

### Ďalšie Kroky

1. Nastaviť pravidelné DB backupy
2. Nakonfigurovať monitoring (ak je potrebné)
3. Pridať ďalších adminov cez `/admin/users`
4. Otestovať s reálnymi PDF dokumentami
5. Škálovať podľa potreby (traffic, storage)

---

**Projekt odovzdaný:** 9. december 2024  
**Status:** ✅ Production-ready  
**Verzía:** 1.0

_"Prvý AI Claims asistent v súlade s EU právom"_

