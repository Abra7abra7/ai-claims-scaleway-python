# AI Claims Processing System - Handover Dokumentacia

**Datum odovzdania:** December 2024  
**Status:** Production-ready

---

## Obsah

1. [Uvod a Kontext](#uvod-a-kontext)
2. [Historia Vyvoja](#historia-vyvoja)
3. [Architektura Systemu](#architektura-systemu)
4. [Bezpecnost](#bezpecnost)
5. [Workflow Spracovania](#workflow-spracovania)
6. [Sprava Systemu](#sprava-systemu)
7. [Buduci Vyvoj](#buduci-vyvoj)

**Prakticke navody (vyvoj, deployment, troubleshooting):** [QUICKSTART.md](QUICKSTART.md)

---

## Uvod a Kontext

### Co je AI Claims?

AI Claims Processing System je AI asistent pre spracovanie poistnych udalosti v sulade s EU pravom. Automatizuje spracovanie PDF dokumentov od OCR extrakcie az po AI analyzu s GDPR compliance.

### Preco vznikol?

System vznikol pre regulovane prostredie poistovne:
- Automatizovane spracovanie poistnych udalosti
- GDPR anonymizacia osobnych udajov
- Human-in-the-loop kontrolne body
- Kompletny audit trail vsetkych akcii
- Bezpecna authentifikacia a session management

### Pre koho je urceny?

- **Claims handlers** - spracovanie poistnych udalosti
- **Compliance officers** - audit log monitoring
- **IT admins** - sprava pouzivatelov a systemu

---

## Historia Vyvoja

### Timeline

| Datum | Udalost |
|-------|---------|
| **19. november 2024** | Zaciatok vyvoja, prvy commit |
| **Tyzden 1-2** | Zakladna architektura (FastAPI + Next.js) |
| **Tyzden 2** | Scaleway integracia - pivot na lokalny vyvoj |
| **Tyzden 3** | Enterprise authentifikacia + email flows |
| **December 2024** | Production deployment, handover |

### Historia Hostingu

**Faza 1: Scaleway (november 2024)**
- Plan: Cloud hosting na Scaleway (Managed PostgreSQL, S3)
- Problem: Poplatky zacinali okamzite
- Rozhodnutie: Pivot na lokalny vyvoj

**Faza 2: Lokalny vyvoj (november 2024)**
- MinIO namiesto Scaleway S3
- Lokalny PostgreSQL v Docker
- Moznost prepnut spat na Scaleway v buducnosti

**Faza 3: IBM Server v Novis (december 2024) - AKTUALNE**
- Server: 10.85.55.26
- URL: https://ai-claims.novis.eu
- Storage: MinIO (moznost upgrade na Scaleway)
- Database: PostgreSQL + pgvector

---

## Architektura Systemu

### Prehlad Komponentov

```
Frontend (Next.js)  ------->  Backend (FastAPI)  ------->  PostgreSQL
    :3000                         :8000                      :5432
                                     |
                      +--------------+---------------+
                      |              |               |
                   Worker         Redis          Presidio
                  (Celery)        :6379           :8001
                      |
                      v
                   MinIO
                (S3 Storage)
```

### Docker Services

| Service | Port | Ucel |
|---------|------|------|
| Frontend | 3000 | Next.js web aplikacia |
| Backend | 8000 | FastAPI REST API |
| Worker | - | Celery background tasks |
| Database | 5432 | PostgreSQL + pgvector |
| Redis | 6379 | Queue a cache |
| MinIO | 9000/9001 | S3 Object storage |
| Presidio | 8001 | PII anonymization |
| pgAdmin | 5050 | Database UI |

### Tech Stack

| Vrstva | Technologie |
|--------|-------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind, shadcn/ui, next-intl |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0, Pydantic v2 |
| **Database** | PostgreSQL 16 + pgvector |
| **Storage** | MinIO / Scaleway S3 |
| **Queue** | Redis 7 + Celery 5 |
| **AI** | Mistral AI (GDPR), Google Gemini, OpenAI, Microsoft Presidio |

### API Endpoints

Kompletny zoznam v Swagger: `/api/v1/docs`

Hlavne sekcie:
- `/api/v1/auth/*` - Authentifikacia
- `/api/v1/claims/*` - Claims CRUD
- `/api/v1/ocr/*` - OCR review
- `/api/v1/anonymization/*` - Anonymization review
- `/api/v1/analysis/*` - AI analyza
- `/api/v1/rag/*` - Policy documents
- `/api/v1/reports/*` - Report management
- `/api/v1/audit/*` - Audit logs

---

## Bezpecnost

### Authentifikacia

**Preco vlastny auth?**
- Regulovane prostredie - potreba plnej kontroly
- Audit logging - kazda akcia musi byt zalogovana
- Session management - IP + User-Agent tracking
- GDPR compliance - plna kontrola nad user data

**Ako funguje:**

1. **Registracia:** User vyplni formular, backend vytvori ucet, posle verification email
2. **Email Verification:** User klikne link, token sa overi, `email_verified = TRUE`
3. **Login:** Overi credentials, vytvori DB session, HTTP-only cookie
4. **Session Management:** Session v PostgreSQL, 7 dni platnost, moznost revoke
5. **Password Reset:** Jednorązovy token (1h), auto-verify email, revoke sessions

### Bezpecnostne Vlastnosti

- PBKDF2-SHA256 password hashing (100,000 iteracii)
- HTTP-only cookies (nie localStorage)
- Session tokens v DB (okamzity revoke)
- Email verification povinna
- IP address logging
- User-Agent tracking
- Audit trail kazdej akcie
- CORS konfigurovany pre production domain

### Role-Based Access Control

- **USER** - zakladne opravnenia (view claims, upload documents)
- **ADMIN** - plne opravnenia (user management, audit logs, system stats)

### GDPR Compliance

1. PII Anonymizacia - Microsoft Presidio (SK, IT, DE)
2. Audit Logging - kazda akcia zalogovana
3. Right to be forgotten - moznost vymazat user data
4. Data minimization - len potrebne udaje
5. Secure sessions - DB-based, revocable

### Audit Logging

Kazda akcia je zalogovana v `audit_logs` tabulke:

- REGISTER_SUCCESS / REGISTER_FAILED
- LOGIN_SUCCESS / LOGIN_FAILED
- LOGOUT
- EMAIL_VERIFIED
- PASSWORD_CHANGED / PASSWORD_RESET_*
- CLAIM_CREATED / CLAIM_UPDATED / CLAIM_DELETED
- OCR_APPROVED / OCR_REJECTED
- ANON_APPROVED / ANON_REJECTED
- ANALYSIS_STARTED / ANALYSIS_COMPLETED

---

## Workflow Spracovania Poistnej Udalosti

```
1. UPLOAD
   User: Nahra PDF dokument
   Status: UPLOADED

2. OCR EXTRACTION
   Worker: Mistral AI Document OCR
   Status: OCR_PROCESSING -> OCR_COMPLETED

3. DATA CLEANING
   Worker: Pravidlove cistenie OCR sumu
   Status: CLEANING

4. HUMAN REVIEW #1 - OCR
   User: Skontroluje a upravi extrahovany text
   Status: OCR_REVIEW_NEEDED -> OCR_APPROVED

5. ANONYMIZACIA
   Worker: Presidio anonymizacia (SK/IT/DE)
   Status: ANONYMIZATION_PROCESSING

6. HUMAN REVIEW #2 - ANONYMIZACIA
   User: Skontroluje side-by-side
   Status: ANON_REVIEW_NEEDED -> ANON_APPROVED

7. AI ANALYZA
   Worker: RAG-enhanced AI analyza
   Status: ANALYSIS_STARTED -> ANALYSIS_COMPLETED

8. PDF REPORT
   System: Automaticky generuje PDF report
   Status: COMPLETED

9. AUDIT LOG
   System: Kazdy krok zalogovany
```

### Stavy Claimu

| Status | Popis | Dalsi krok |
|--------|-------|------------|
| UPLOADED | Dokument nahrany | OCR spracovanie |
| OCR_PROCESSING | OCR prebieha | Caka na dokoncenie |
| OCR_COMPLETED | OCR hotove | Human review |
| OCR_REVIEW_NEEDED | Caka na kontrolu | User approves |
| OCR_APPROVED | OCR schvalene | Anonymizacia |
| ANONYMIZATION_PROCESSING | Anonymizacia prebieha | Caka na dokoncenie |
| ANON_REVIEW_NEEDED | Caka na anon kontrolu | User approves |
| ANON_APPROVED | Anon schvalene | AI analyza |
| ANALYSIS_STARTED | Analyza prebieha | Caka na dokoncenie |
| ANALYSIS_COMPLETED | Analyza hotova | Report ready |
| COMPLETED | Vsetko hotove | Archivovane |
| FAILED | Chyba v procese | Manual retry |

---

## Sprava Systemu

### Sprava Pouzivatelov

**Vytvorit admin usera:**
```bash
docker-compose exec backend python scripts/init_admin.py
```

**Zmenit rolu usera na ADMIN:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
"
```

**Manualne verifikovat email:**
```sql
docker-compose exec db psql -U claims_user -d claims_db -c "
UPDATE users SET email_verified = TRUE WHERE email = 'user@example.com';
"
```

### Zalohovanie

**Database backup:**
```bash
docker-compose exec db pg_dump -U claims_user claims_db > backup.sql
```

**Database restore:**
```bash
cat backup.sql | docker-compose exec -T db psql -U claims_user -d claims_db
```

### Monitoring

**Health Checks:**
```bash
curl http://localhost:8000/api/v1/health   # Backend
curl http://localhost:8001/health          # Presidio
```

**Logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f worker
```

**Audit Log:**
- Frontend: `/audit` (admin only)
- Database: `SELECT * FROM audit_logs ORDER BY timestamp DESC;`

---

## Buduci Vyvoj

### Planovane Features

**Priorita 1 (Security):**
- Two-Factor Authentication (TOTP)
- OAuth providers (Google, Microsoft)
- API rate limiting

**Priorita 2 (Features):**
- Batch upload (multiple PDFs)
- Export reports (Excel, JSON)
- Advanced analytics dashboard
- Custom prompt templates

**Priorita 3 (Infrastructure):**
- Prepnut na Scaleway (ak budget dovoli)
- Automated DB backups
- Performance monitoring (Grafana)

### Technicky Dlh

- Unit tests (pytest)
- Integration tests
- CI/CD pipeline (GitHub Actions)
- Code coverage monitoring

---

## Dolezite Subory

### Konfiguracia

| Subor | Ucel |
|-------|------|
| `.env` / `.env.local` | Environment variables |
| `docker-compose.yml` | Base Docker config |
| `docker-compose.local.yml` | Local development overrides |
| `docker-compose.prod.yml` | Production overrides |
| `app/core/config.py` | Backend settings |

### Scripts

| Script | Ucel |
|--------|------|
| `start-local.ps1` | Spustit lokalne (Windows) |
| `start-prod.ps1` | Spustit production (Windows) |
| `scripts/init_admin.py` | Vytvorit admin usera |

### Dokumentacia

| Dokument | Obsah |
|----------|-------|
| `README.md` | Rychly prehlad |
| `docs/QUICKSTART.md` | Vyvoj, deployment, troubleshooting |
| `docs/HANDOVER.md` | Historia, architektura, bezpecnost |
| `docs/ARCHITECTURE.md` | Detailna technicka dokumentacia |

---

## Kontakty

### Repository
- GitHub: https://github.com/Abra7abra7/ai-claims-scaleway-python

### Pristupy

**Lokalny vyvoj:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1/docs
- pgAdmin: http://localhost:5050
- MinIO: http://localhost:9001

**Production:**
- Frontend: https://ai-claims.novis.eu
- Server SSH: ssh user@10.85.55.26

---

**Projekt odovzdany:** December 2024  
**Status:** Production-ready
