# AI Claims Processing System

**AI asistent pre spracovanie poistnych udalosti v sulade s EU pravom**

Automatizovane spracovanie PDF dokumentov s GDPR anonymizaciou a AI analyzou.

---

## Dokumentacia

| Dokument | Popis |
|----------|-------|
| **[QUICKSTART.md](docs/QUICKSTART.md)** | Lokalny vyvoj, deployment, troubleshooting |
| **[HANDOVER.md](docs/HANDOVER.md)** | Historia projektu, architekturne rozhodnutia |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Detailna technicka dokumentacia |

---

## Rychly Start

### Windows

```powershell
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python
Copy-Item .env.example .env.local
.\start-local.ps1
```

### Linux / Mac

```bash
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python
cp .env.example .env.local
make local
```

**Hotovo!** Otvor http://localhost:3000

Detailny navod: [docs/QUICKSTART.md](docs/QUICKSTART.md)

---

## Architektura

```
Frontend (Next.js)  ─────▶  Backend (FastAPI)  ─────▶  PostgreSQL
    :3000                       :8000                    :5432
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                 Worker        Redis         Presidio
                (Celery)       :6379           :8001
                    │
                    ▼
                 MinIO
              (S3 Storage)
```

---

## Hlavne Funkcie

- **Enterprise Auth** - DB sessions, email verification, audit trail
- **OCR** - Mistral AI Document OCR
- **GDPR Anonymizacia** - Microsoft Presidio (SK, IT, DE)
- **Human-in-the-Loop** - Manualne kontrolne body
- **AI Analyza** - RAG-enhanced (Mistral, Gemini, OpenAI)
- **PDF Reporty** - Automaticke generovanie
- **Audit Logging** - Kompletny trail

---

## Tech Stack

| Vrstva | Technologie |
|--------|-------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind, shadcn/ui |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2.0 |
| **Database** | PostgreSQL 16 + pgvector |
| **Storage** | MinIO / Scaleway S3 |
| **AI** | Mistral AI (GDPR), Gemini, OpenAI |
| **Infrastructure** | Docker + Docker Compose |

---

## Produkcia

**URL:** https://ai-claims.novis.eu  
**Server:** IBM infrastructure v Novis

```bash
ssh user@10.85.55.26
cd ~/ai-claims-scaleway-python
git pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Uzitocne Prikazy

```bash
# Status
docker compose ps

# Logy
docker compose logs -f backend

# Restart
docker compose restart backend

# Cistenie
docker compose down
docker system prune -af
```

---

**Posledna aktualizacia:** December 2024  
**Status:** Production-ready
