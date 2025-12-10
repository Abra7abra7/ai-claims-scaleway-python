# 🤖 AI Claims Processing System

**Prvý AI asistent pre spracovanie poistných udalostí v súlade s EU právom**

Inteligentný systém pre regulované prostredie poisťovne s automatizovaným spracovaním PDF dokumentov, GDPR anonymizáciou, a AI analýzou s plným audit loggingom.

---

**📚 Kompletná dokumentácia:** [`docs/HANDOVER.md`](docs/HANDOVER.md)  
**🏗️ Technická architektúra:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)  
**👨‍💻 Development guide:** [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)  
**🚀 Production deployment:** [`docs/PRODUCTION_DEPLOYMENT.md`](docs/PRODUCTION_DEPLOYMENT.md)

## ✨ Hlavné Funkcie

- **🔐 Enterprise Auth** - Bezpečná autentifikácia s DB sessions, IP logging, audit trail
- **🔍 OCR Spracovanie** - Automatická extrakcia textu z PDF dokumentov (Mistral AI Document OCR)
- **🧹 Data Cleaning** - Pravidlové čistenie a normalizácia OCR výstupu
- **🔒 GDPR Anonymizácia** - Country-specific anonymizácia pomocou Microsoft Presidio (SK, IT, DE)
- **👤 Human-in-the-Loop** - Manuálne kontrolné body pre OCR a anonymizáciu
- **🤖 AI Analýza** - RAG-enhanced analýza s podporou viacerých AI providerov (Mistral - GDPR compliant, Gemini, OpenAI)
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

### Lokálny Vývoj (4 kroky)

```bash
# 1. Clone repository
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 2. Nakonfiguruj .env súbor
cp .env.example .env
# Vyplň: SMTP credentials, MISTRAL_API_KEY (GDPR compliant)

# 3. Spusti Docker služby
docker-compose up -d

# 4. Vytvor admin používateľa
docker-compose exec backend python scripts/init_admin.py
```

**Hotovo!** Otvor http://localhost:3000 a prihlás sa:
- Email: `admin@example.com`
- Password: `admin123`

### Production Deployment (IBM Server v Novis)

```bash
# SSH do servera
ssh user@10.85.55.26

# Pull najnovšie zmeny
cd /path/to/ai-claims
git pull

# Spusti s production konfiguráciou
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**URL:** https://ai-claims.novis.eu

Kompletný deployment návod: [`docs/PRODUCTION_DEPLOYMENT.md`](docs/PRODUCTION_DEPLOYMENT.md)

## 🔐 Bezpečnosť & Autentifikácia

### Enterprise-Grade Auth
- ✅ **PBKDF2-SHA256** password hashing (100k iterácií)
- ✅ **DB-based sessions** uložené v PostgreSQL (nie JWT v localStorage)
- ✅ **HTTP-only cookies** pre session tokens
- ✅ **Email verification** povinná pred prihlásením
- ✅ **Password reset** cez email s jednorázovými tokenmi
- ✅ **IP + User-Agent logging** pre každú session
- ✅ **Session management** - možnosť odhlásiť konkrétne zariadenia
- ✅ **Audit trail** každej akcie (GDPR compliance)
- ✅ **Role-based access** (ADMIN, USER)

### GDPR Compliance
- ✅ **PII anonymizácia** cez Microsoft Presidio (country-specific: SK, IT, DE)
- ✅ **Kompletný audit log** všetkých akcií
- ✅ **Data minimization** - len potrebné údaje
- ✅ **Right to be forgotten** - možnosť vymazať user data

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 16, React 19, TypeScript 5, Tailwind CSS, shadcn/ui, next-intl |
| **Backend** | FastAPI 0.100+, Python 3.11, Pydantic v2, SQLAlchemy 2.0 |
| **Database** | PostgreSQL 16 + pgvector extension |
| **Storage** | MinIO (S3-compatible) / Scaleway Object Storage |
| **Queue** | Redis 7 + Celery 5 |
| **AI Services** | Mistral AI (GDPR), Google Gemini, OpenAI, Microsoft Presidio |
| **Infrastructure** | Docker + Docker Compose |
| **Current Hosting** | IBM Server v Novis (10.85.55.26) |

Kompletný tech stack: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## 📋 Workflow Spracovania Poistnej Udalosti

```
1. 📤 Upload PDF
   ↓
2. 🔍 OCR Extrakcia (Mistral AI)
   ↓
3. 👁️ Human Review #1 (OCR kontrola)
   ↓
4. 🧹 Data Cleaning (pravidlové čistenie)
   ↓
5. 🔒 Anonymizácia (Presidio - country-specific)
   ↓
6. 👁️ Human Review #2 (anonymizácia kontrola)
   ↓
7. 🤖 AI Analýza (RAG-enhanced)
   ↓
8. 📄 PDF Report Generovanie
   ↓
9. ✅ Hotovo (audit log každého kroku)
```

Detailný workflow: [`docs/HANDOVER.md#workflow`](docs/HANDOVER.md#workflow-spracovania-poistnej-udalosti)

## 📊 Aktuálny Stav

**Status:** ✅ Production-ready (9. december 2024)

| Komponent | Status |
|-----------|--------|
| Frontend (Next.js) | ✅ Funkčný |
| Backend (FastAPI) | ✅ Funkčný |
| Autentifikácia | ✅ Enterprise-ready |
| Email flows | ✅ Funkčné (verification + password reset) |
| OCR spracovanie | ✅ Funkčné (Mistral AI) |
| Anonymizácia | ✅ Funkčná (Presidio SK/IT/DE) |
| AI analýza | ✅ Funkčná (RAG-enhanced) |
| PDF reporty | ✅ Funkčné |
| Audit logging | ✅ Kompletný trail |
| Multi-language | ✅ SK/EN |

**Deployment:** IBM Server v Novis (https://ai-claims.novis.eu)

## 🆘 Riešenie Problémov

**Dokumentácia:**
- [`docs/HANDOVER.md#riešenie-problémov`](docs/HANDOVER.md#riešenie-problémov) - Časté problémy a riešenia
- [`docs/PRODUCTION_DEPLOYMENT.md`](docs/PRODUCTION_DEPLOYMENT.md) - Deployment troubleshooting
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) - Development guidelines

**Logy:**
```bash
# Backend logs
docker-compose logs -f backend

# Worker logs
docker-compose logs -f worker

# Všetky služby
docker-compose logs -f
```

## 👥 Pre Kolegov

Tento systém je odovzdaný s kompletnou dokumentáciou pre ďalší vývoj a prevádzku.

**Začni tu:** [`docs/HANDOVER.md`](docs/HANDOVER.md)

Dokument obsahuje:
- História vývoja a hostingu (Scaleway → lokálny → IBM)
- Kompletná architektúra
- Bezpečnostné vlastnosti
- Lokálny vývoj setup
- Production deployment
- Správa systému (users, sessions, backups)
- Riešenie problémov
- Budúci vývoj (2FA, OAuth, atď.)

---

**Last Updated:** December 9, 2024  
**Version:** 1.0  
**License:** Proprietary
