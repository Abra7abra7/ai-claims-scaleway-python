# 🤖 AI Claims Processing System

Inteligentný systém na spracovanie poistných udalostí s využitím AI, OCR, anonymizácie a analýzy dokumentov.

## ✨ Hlavné Funkcie

- **🔍 OCR Spracovanie** - Automatická extrakcia textu z PDF dokumentov (Mistral AI Document OCR)
- **🧹 Data Cleaning** - Pravidlové čistenie a normalizácia OCR výstupu
- **🔒 GDPR Anonymizácia** - Country-specific anonymizácia pomocou Microsoft Presidio (SK, IT, DE)
- **👤 Human-in-the-Loop** - Manuálne kontrolné body pre OCR a anonymizáciu
- **🤖 AI Analýza** - RAG-enhanced analýza s podporou viacerých AI providerov (Mistral, Gemini, OpenAI)
- **📄 PDF Reporty** - Automatické generovanie structured PDF reportov
- **📊 Audit Logging** - Kompletný audit trail všetkých zmien
- **☁️ Scaleway Integration** - Managed PostgreSQL + S3 Object Storage
- **🔄 Retry & Recovery** - Manuálny retry pre zaseknuté procesy

## 🏗️ Architektúra

```
┌─────────────┐         ┌──────────────┐
│   Frontend  │────────▶│   Backend    │
│ (Streamlit) │         │  (FastAPI)   │
│ :8501       │         │  :8000       │
└─────────────┘         └──────┬───────┘
                               │
                ┌──────────────┼───────────────┐
                │              │               │
         ┌──────▼──────┐ ┌────▼─────┐  ┌─────▼──────┐
         │   Worker    │ │  Redis   │  │  Presidio  │
         │  (Celery)   │ │  :6379   │  │    API     │
         └──────┬──────┘ └──────────┘  │   :8001    │
                │                       └────────────┘
    ┌───────────┴────────────┐
    │                        │
┌───▼────────────┐  ┌────────▼──────────┐
│  PostgreSQL    │  │  Scaleway S3      │
│  (pgvector)   │  │  Object Storage   │
└────────────────┘  └───────────────────┘
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
./local-start.sh
# Alebo manuálne:
docker compose up -d

# 4. Otvor v prehliadači
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
```

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

## 📖 Dokumentácia

- **[QUICK_START.md](QUICK_START.md)** - Rýchly štart pre lokálny vývoj
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Návod na vývoj a testovanie
- **[docs/DEPLOYMENT_UPDATES.md](docs/DEPLOYMENT_UPDATES.md)** - Ako nasadzovať nové zmeny
- **[deploy/README.md](deploy/README.md)** - Produkčný deployment na Scaleway
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment checklist
- **[CHANGELOG_FIX.md](CHANGELOG_FIX.md)** - História opráv a zmien

## 🛠️ Tech Stack

**Backend:** FastAPI, SQLAlchemy, Celery, Pydantic  
**Frontend:** Streamlit  
**AI & ML:** Mistral AI, Google Gemini, OpenAI (modulárna podpora), Microsoft Presidio, pgvector  
**Infrastructure:** Docker, PostgreSQL, Redis, S3  
**Cloud:** Scaleway (Managed PostgreSQL, Object Storage, Compute)

## 🤖 AI Provider Configuration

Systém podporuje **modulárnu architektúru** pre AI providerov. Môžeš jednoducho prepínať medzi rôznymi LLM službami bez zmeny kódu.

### Podporované Provideri

- **Mistral AI** - Pre OCR a LLM analýzu
- **Google Gemini** - Pre LLM analýzu (gemini-1.5-pro, gemini-1.5-flash)
- **OpenAI** - Pre LLM analýzu (gpt-4-turbo, gpt-3.5-turbo) - *Plánované*

### Konfigurácia Providera

V `.env` súbore nastav:

```env
# Vyber providera pre LLM (analýza textu)
LLM_PROVIDER=gemini  # možnosti: mistral, openai, gemini

# Voliteľne: špecifická verzia modelu
LLM_MODEL_VERSION=gemini-1.5-flash

# Provider pre OCR (extrakcia textu z PDF)
OCR_PROVIDER=mistral  # aktuálne podporované: mistral
```

**Výhody:**
- ✅ Jednoduché prepínanie providerov bez zmeny kódu
- ✅ Všetky API kľúče môžu byť v `.env` súčasne
- ✅ Fallback na default provider ak je problém
- ✅ Konzistentné API cez všetkých providerov

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

Potrebné premenné v `.env` súbore:

```env
# ==============================================
# 🤖 AI PROVIDER SELECTION
# ==============================================
LLM_PROVIDER=mistral  # mistral, openai, gemini
LLM_MODEL_VERSION=mistral-small-latest  # Voliteľné
OCR_PROVIDER=mistral

# ==============================================
# 🔑 API KEYS
# ==============================================
MISTRAL_API_KEY=your_mistral_key
OPENAI_API_KEY=your_openai_key  # Voliteľné
GEMINI_API_KEY=your_gemini_key  # Voliteľné

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

## 🔄 Retry & Recovery

Systém obsahuje zabudované mechanizmy na zotavenie z chýb:

- **Retry Anonymization** - Pre zaseknuté anonymizačné procesy
- **Reset Analysis Status** - Pre zaseknuté alebo zlyhané analýzy
- **Automatické error handling** - Failed claims sú označené a môžu byť reštartované

## 🤝 Prispievanie

Pozri [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) pre návod na lokálny vývoj a [docs/DEPLOYMENT_UPDATES.md](docs/DEPLOYMENT_UPDATES.md) pre nasadzovanie zmien.

## 📊 Status Projektu

✅ **Produkčný deployment dokončený**  
✅ Všetky služby funkčné  
✅ Presidio anonymizácia funguje  
✅ RAG systém implementovaný  
✅ PDF report generation  
✅ Modulárna podpora AI providerov (Mistral, Gemini)  
✅ Retry & Recovery mechanizmy

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
