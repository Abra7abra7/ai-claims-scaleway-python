# AI Claims Processing System - Scaleway PoC

Automatizovaný systém pre spracovanie poistných nárokov pomocou AI. Využíva Mistral AI pre OCR a analýzu, Microsoft Presidio pre anonymizáciu a Scaleway pre hosting.

## ✨ Funkcie

- 📄 **Multi-file Upload** - Nahrávanie viacerých PDF dokumentov do jedného nároku
- 🔍 **OCR** - Automatická extrakcia textu pomocou Mistral Document AI
- 🔒 **Anonymizácia** - Ochrana citlivých údajov (mená, rodné čísla, IBAN, telefóny, emaily)
- 🤖 **AI Analýza** - 5 typov analýz pomocou Mistral AI:
  - Štandardná analýza
  - Detailná zdravotná analýza
  - Detekcia podvodov
  - Rýchle posúdenie
  - Slovenská analýza
- 📊 **Admin Dashboard** - Prehľad a správa nárokov
- ⚡ **Async Processing** - Celery workers pre paralelné spracovanie

## 🏗️ Architektúra

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Streamlit  │─────▶│   FastAPI    │─────▶│   Celery    │
│  Frontend   │      │   Backend    │      │   Worker    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │  PostgreSQL  │      │  Mistral AI │
                     │  + pgvector  │      │     API     │
                     └──────────────┘      └─────────────┘
                            │                      
                            ▼                      
                     ┌──────────────┐      
                     │   Scaleway   │      
                     │  S3 Storage  │      
                     └──────────────┘      
```

## 🚀 Quick Start

### Predpoklady

- Docker & Docker Compose
- Mistral AI API key
- Scaleway Object Storage (S3) credentials

### Lokálne spustenie

1. **Klonovanie repozitára**
```bash
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python
```

2. **Konfigurácia environment variables**
```bash
cp .env.example .env
# Upravte .env s vašimi API keys
```

3. **Spustenie služieb**
```bash
docker compose up -d
```

4. **Prístup k aplikácii**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/docs

## 📚 Dokumentácia

- **[Architektúra](docs/ARCHITECTURE.md)** - Detailný popis komponentov a workflow
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Návod na nasadenie na Scaleway
- **[User Guide](docs/USER_GUIDE.md)** - Používateľská príručka
- **[Scaleway Setup](docs/scaleway_setup.md)** - Manuálna konfigurácia Scaleway

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Database:** PostgreSQL + pgvector
- **Queue:** Celery + Redis
- **Storage:** Scaleway Object Storage (S3-compatible)
- **AI:** Mistral AI (OCR, Embeddings, Chat)
- **Anonymization:** Microsoft Presidio
- **Deployment:** Docker Compose

## 📋 Environment Variables

```bash
# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key

# Scaleway Object Storage
S3_ACCESS_KEY=your_scaleway_access_key
S3_SECRET_KEY=your_scaleway_secret_key
S3_BUCKET_NAME=ai-claims-docs
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

# Database (Docker Compose default)
DATABASE_URL=postgresql://postgres:postgres@db:5432/claims_db

# Redis (Docker Compose default)
REDIS_URL=redis://redis:6379/0
```

## 🔧 Užitočné príkazy

```bash
# Spustenie služieb
docker compose up -d

# Sledovanie logov
docker compose logs -f

# Reštart služieb
docker compose restart

# Zastavenie služieb
docker compose down

# Záloha databázy
docker compose exec db pg_dump -U postgres claims_db > backup.sql

# Verifikácia pripojení
docker compose exec backend python scripts/verify_connections.py
```

## 📊 Workflow

1. **Upload** - Používateľ nahrá PDF dokumenty
2. **OCR** - Mistral AI extrahuje text z dokumentov
3. **Anonymizácia** - Presidio anonymizuje citlivé údaje
4. **Čakanie** - Nárok čaká na schválenie adminom
5. **Analýza** - Admin vyberie typ analýzy a schváli
6. **Výsledok** - AI poskytne odporúčanie, confidence a reasoning

## 🔒 Bezpečnosť

- ✅ Anonymizácia pred odoslaním do AI
- ✅ Private S3 bucket
- ✅ Presigned URLs (časovo obmedzené)
- ✅ Environment variables pre credentials
- ✅ Slovak-specific PII recognizers

## 💰 Náklady (Scaleway PoC)

- VM (DEV1-M): ~€7-10/mesiac
- Object Storage (10GB): ~€0.20/mesiac
- Flexible IP: €1/mesiac
- **Celkom: ~€8-12/mesiac** (bez Mistral API usage)

## 🤝 Príspevky

Príspevky sú vítané! Prosím vytvorte issue alebo pull request.

## 📝 Licencia

MIT License

## 👨‍💻 Autor

Vytvorené pre Scaleway PoC

## 🆘 Podpora

- GitHub Issues: https://github.com/Abra7abra7/ai-claims-scaleway-python/issues
- Dokumentácia: [docs/](docs/)

## 📅 Changelog

### v1.0.0 (2024-11-19)
- ✨ Prvé vydanie
- ✨ Multi-file upload do jedného claim
- ✨ OCR pomocou Mistral Document AI
- ✨ Anonymizácia pomocou Microsoft Presidio
- ✨ 5 typov AI analýz
- ✨ Streamlit frontend
- ✨ FastAPI backend
- ✨ Celery async processing
- ✨ Globálny systém promptov
