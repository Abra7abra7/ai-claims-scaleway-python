# 🤖 AI Claims Processing System

Inteligentný systém na spracovanie poistných udalostí s využitím AI, OCR, anonymizácie a analýzy dokumentov.

**Pre regulované prostredie (poisťovňa)** s plným audit loggingom a bezpečnou autentifikáciou.

## ✨ Hlavné Funkcie

- **🔐 Enterprise Auth** - Bezpečná autentifikácia s DB sessions, IP logging, audit trail
- **🔍 OCR Spracovanie** - Automatická extrakcia textu z PDF dokumentov (Mistral AI Document OCR)
- **🧹 Data Cleaning** - Pravidlové čistenie a normalizácia OCR výstupu
- **🔒 GDPR Anonymizácia** - Country-specific anonymizácia pomocou Microsoft Presidio (SK, IT, DE)
- **👤 Human-in-the-Loop** - Manuálne kontrolné body pre OCR a anonymizáciu
- **🤖 AI Analýza** - RAG-enhanced analýza s podporou viacerých AI providerov (Mistral, Gemini, OpenAI)
- **📄 PDF Reporty** - Automatické generovanie structured PDF reportov
- **📊 Audit Logging** - Kompletný audit trail všetkých zmien (GDPR compliant)
- **☁️ Scaleway Integration** - Managed PostgreSQL + S3 Object Storage
- **🌍 Multi-language UI** - Podpora SK/EN s next-intl
- **🔄 Retry & Recovery** - Manuálny retry pre zaseknuté procesy

## 🏗️ Architektúra

```
┌─────────────┐         ┌──────────────┐
│   Frontend  │────────▶│   Backend    │
│  (Next.js)  │         │  (FastAPI)   │
│   :3000     │         │  :8000       │
└─────────────┘         └──────┬───────┘
      │                        │
      │                        │
      │         ┌──────────────┼───────────────┐
      │         │              │               │
      │   ┌─────▼──────┐ ┌────▼─────┐  ┌─────▼──────┐
      │   │   Worker   │ │  Redis   │  │  Presidio  │
      │   │  (Celery)  │ │  :6379   │  │    API     │
      │   └─────┬──────┘ └──────────┘  │   :8001    │
      │         │                       └────────────┘
      │    ┌────┴─────────────┐
      │    │                  │
      │ ┌──▼──────────────┐  ┌▼─────────────────┐
      └▶│   PostgreSQL    │  │  Scaleway S3     │
        │   (pgvector)    │  │  Object Storage  │
        │   + Auth DB     │  └──────────────────┘
        └─────────────────┘
```

## 🚀 Rýchly Štart

### Lokálny Vývoj

```bash
# 1. Clone repository
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 2. Vytvor .env súbor (pozri .env.example)
cp .env.example .env
# Vyplň potrebné credentials

# 3. Spusti služby
docker compose up -d

# 4. Vytvor admin používateľa (prvýkrát)
docker compose exec backend python -c "
from app.db.session import SessionLocal
from app.db.models import User, UserRole
from app.services.auth import hash_password
db = SessionLocal()
admin = User(
    email='admin@example.com',
    password_hash=hash_password('admin123456'),
    name='Admin',
    role='admin',
    locale='sk',
    is_active=True,
    email_verified=True
)
db.add(admin)
db.commit()
print('Admin created!')
db.close()
"

# 5. Otvor v prehliadači
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/v1/docs
```

### Prihlasovacie údaje (demo)

```
Email: admin@example.com
Password: admin123456
```

⚠️ **Zmeňte heslo po prvom prihlásení!**

Detailný návod: [QUICK_START.md](QUICK_START.md)

### Produkčné Nasadenie na Scaleway

```bash
# Na Scaleway serveri
cd /opt/ai-claims
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git .

# Vytvor .env súbor
nano .env

# Spusti deployment
chmod +x deploy/install.sh
./deploy/install.sh
```

Kompletný guide: [deploy/README.md](deploy/README.md)

## 🔐 Autentifikácia (Enterprise)

Systém obsahuje bezpečnú autentifikáciu vhodnú pre regulované prostredie:

### Funkcie

| Funkcia | Popis |
|---------|-------|
| **DB Sessions** | Sessions uložené v PostgreSQL |
| **IP Logging** | Každé prihlásenie zaznamenáva IP a User-Agent |
| **Audit Trail** | LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT, PASSWORD_CHANGED |
| **Session Management** | Možnosť odhlásiť konkrétne zariadenie |
| **Role-based Access** | ADMIN, USER, VIEWER |
| **Account Lock** | Admin môže zablokovať účet |
| **Inactivity Timeout** | Automatické odhlásenie po 24h nečinnosti |

### Auth API Endpoints

```
POST /api/v1/auth/register     - Registrácia
POST /api/v1/auth/login        - Prihlásenie
POST /api/v1/auth/logout       - Odhlásenie
GET  /api/v1/auth/me           - Info o používateľovi
POST /api/v1/auth/password/change - Zmena hesla
GET  /api/v1/auth/sessions     - Aktívne sessions
POST /api/v1/auth/sessions/{id}/revoke - Zrušiť session
POST /api/v1/auth/sessions/revoke-all - Odhlásiť všade

# Admin endpoints
GET  /api/v1/auth/admin/users
POST /api/v1/auth/admin/users/{id}/disable
POST /api/v1/auth/admin/users/{id}/enable
```

## 📖 Dokumentácia

- **[QUICK_START.md](QUICK_START.md)** - Rýchly štart pre lokálny vývoj
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Návod na vývoj a testovanie
- **[docs/DEPLOYMENT_UPDATES.md](docs/DEPLOYMENT_UPDATES.md)** - Ako nasadzovať nové zmeny
- **[docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)** - Aktuálny stav projektu
- **[deploy/README.md](deploy/README.md)** - Produkčný deployment na Scaleway
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment checklist
- **[CHANGELOG_FIX.md](CHANGELOG_FIX.md)** - História opráv a zmien

## 🛠️ Tech Stack

**Backend:** FastAPI, SQLAlchemy, Celery, Pydantic, PBKDF2 password hashing  
**Frontend:** Next.js 16, React 19, TailwindCSS v4, shadcn/ui, next-intl  
**AI & ML:** Mistral AI, Google Gemini, OpenAI (modulárna podpora), Microsoft Presidio, pgvector  
**Auth:** Custom DB sessions, HTTP-only cookies, role-based access  
**Infrastructure:** Docker, PostgreSQL, Redis, S3  
**Cloud:** Scaleway (Managed PostgreSQL, Object Storage, Compute)

## 🤖 AI Provider Configuration

Systém podporuje **modulárnu architektúru** pre AI providerov.

### Podporované Provideri

- **Mistral AI** - Pre OCR a LLM analýzu
- **Google Gemini** - Pre LLM analýzu (gemini-1.5-pro, gemini-1.5-flash)
- **OpenAI** - Pre LLM analýzu (gpt-4-turbo, gpt-3.5-turbo)

### Konfigurácia

```env
LLM_PROVIDER=gemini  # mistral, openai, gemini
LLM_MODEL_VERSION=gemini-1.5-flash
OCR_PROVIDER=mistral
```

## 📋 Workflow

1. **Upload** → Nahranie PDF dokumentov
2. **OCR** → Extrakcia textu (Mistral Document AI)
3. **OCR Review** → Human-in-the-Loop kontrola
4. **Cleaning** → Čistenie a normalizácia textu
5. **Anonymization** → PII removal (Presidio)
6. **Anonymization Review** → Human-in-the-Loop kontrola
7. **AI Analysis** → Analýza s RAG (vybraný LLM provider)
8. **Report** → Generovanie PDF reportu

## 🔐 Environment Variables

```env
# ==============================================
# 🔐 AUTH
# ==============================================
BETTER_AUTH_SECRET=your-32-char-secret

# ==============================================
# 🤖 AI PROVIDER SELECTION
# ==============================================
LLM_PROVIDER=mistral
OCR_PROVIDER=mistral

# ==============================================
# 🔑 API KEYS
# ==============================================
MISTRAL_API_KEY=your_mistral_key
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# ==============================================
# ☁️ SCALEWAY STORAGE & DATABASE
# ==============================================
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket_name
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://redis:6379/0
PRESIDIO_URL=http://presidio:8001
```

**Nikdy necommituj `.env` súbor do Gitu!**

## 📊 Status Projektu

✅ **Produkčný deployment dokončený**  
✅ Všetky služby funkčné  
✅ Backend autentifikácia s audit logom  
✅ Presidio anonymizácia funguje  
✅ RAG systém implementovaný  
✅ PDF report generation  
✅ Modulárna podpora AI providerov (Mistral, Gemini)  
✅ Retry & Recovery mechanizmy  
✅ Next.js 16 frontend s dark theme  
✅ Multi-language support (SK/EN)

## 🆘 Support & Troubleshooting

**Časté problémy a riešenia:**
- [QUICK_START.md - Troubleshooting sekcia](QUICK_START.md#troubleshooting)
- [DEPLOYMENT_CHECKLIST.md - Troubleshooting guide](DEPLOYMENT_CHECKLIST.md#troubleshooting)

**Kontakt:** Otvor issue na GitHube

## 📝 Licencia

Proprietary - All rights reserved

---

**Projekt je nasadený a funguje na Scaleway infraštruktúre.**  
Pre viac informácií pozri dokumentáciu v `/docs` priečinku.

**Last updated:** 2024-12-09
