# 🤖 AI Claims Processing System

Inteligentný systém na spracovanie poistných udalostí s využitím AI, OCR, anonymizácie a analýzy dokumentov.

## ✨ Hlavné Funkcie

- **🔍 OCR Spracovanie** - Automatická extrakcia textu z PDF dokumentov pomocou Mistral AI
- **🧹 Data Cleaning** - Pravidlové čistenie a normalizácia OCR výstupu
- **🔒 GDPR Anonymizácia** - Country-specific anonymizácia pomocou Microsoft Presidio (SK, IT, DE)
- **👤 Human-in-the-Loop** - Manuálne kontrolné body pre OCR a anonymizáciu
- **🤖 AI Analýza** - RAG-enhanced analýza s Mistral AI a 5 preddefinovanými promptami
- **📄 PDF Reporty** - Automatické generovanie structured PDF reportov
- **📊 Audit Logging** - Kompletný audit trail všetkých zmien
- **☁️ Scaleway Integration** - Managed PostgreSQL + S3 Object Storage

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
│  (pgvector)    │  │  Object Storage   │
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
**AI & ML:** Mistral AI, Microsoft Presidio, pgvector  
**Infrastructure:** Docker, PostgreSQL, Redis, S3  
**Cloud:** Scaleway (Managed PostgreSQL, Object Storage, Compute)

## 📋 Workflow

1. **Upload** → Nahranie PDF dokumentov
2. **OCR** → Extrakcia textu (Mistral Vision)
3. **OCR Review** → Human-in-the-Loop kontrola
4. **Cleaning** → Čistenie a normalizácia textu
5. **Anonymization** → PII removal (Presidio)
6. **Anonymization Review** → Human-in-the-Loop kontrola
7. **AI Analysis** → Analýza s RAG (Mistral AI)
8. **Report** → Generovanie PDF reportu

## 🔐 Environment Variables

Potrebné premenné v `.env` súbore:

```env
# Mistral AI
MISTRAL_API_KEY=your_key_here

# Scaleway S3
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket_name
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (internal)
REDIS_URL=redis://redis:6379/0

# Presidio (internal)
PRESIDIO_URL=http://presidio:8001
```

**Nikdy necommituj `.env` súbor do Gitu!**

## 🤝 Prispievanie

Pozri [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) pre návod na lokálny vývoj a [docs/DEPLOYMENT_UPDATES.md](docs/DEPLOYMENT_UPDATES.md) pre nasadzovanie zmien.

## 📊 Status Projektu

✅ **Produkčný deployment dokončený**  
✅ Všetky služby funkčné  
✅ Presidio anonymizácia funguje  
✅ RAG systém implementovaný  
✅ PDF report generation  

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
