# AI Claims - Rýchly Štart

## Lokálny Vývoj

### Požiadavky
- Docker a Docker Compose
- Git
- `.env` súbor s potrebnými credentials

### Rýchle spustenie

```bash
# 1. Clone repozitár
git clone https://github.com/yourusername/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 2. Vytvor .env súbor (pozri .env.example)
# Vyplň všetky potrebné premenné

# 3. Spusti služby
./local-start.sh

# Alebo manuálne:
docker compose build
docker compose up -d
```

### Prístupové URL
- **Frontend (Next.js)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/api/v1/docs
- **Presidio API**: http://localhost:8001
- **MinIO Console**: http://localhost:9001

### Užitočné príkazy

```bash
# Zobraz status služieb
docker compose ps

# Sleduj logy
docker compose logs -f

# Sleduj konkrétnu službu
docker compose logs -f worker

# Reštart služieb
docker compose restart

# Stop všetkých služieb
docker compose down

# Úplný rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Makefile príkazy

```bash
make help       # Zobraz všetky dostupné príkazy
make up         # Spusti služby
make down       # Zastav služby
make logs       # Sleduj logy
make health     # Kontrola zdravia služieb
make migrate    # Spusti databázové migrácie
make rebuild    # Úplný rebuild
```

## Troubleshooting

### Presidio nefunguje
```bash
# Kontrola health statusu
curl http://localhost:8001/health

# Rebuild Presidio
docker compose build --no-cache presidio
docker compose up -d presidio

# Sleduj logy
docker compose logs -f presidio
```

### Worker nemôže kontaktovať Presidio
```bash
# Reštartuj worker s depends_on
docker compose restart worker

# Skontroluj Docker sieť
docker network inspect ai-claims-scaleway-python_default
```

### Database connection error
```bash
# Overit DATABASE_URL v .env
cat .env | grep DATABASE_URL

# Test pripojenia
docker compose exec backend python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('DB OK')"
```

## Nasadenie na Scaleway

Pre detailný návod na produkčné nasadenie, pozri:
- [deploy/README.md](deploy/README.md) - Kompletný deployment guide
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Technická dokumentácia

### Rýchly deployment

```bash
# Na Scaleway serveri:
cd /opt/ai-claims
git clone https://github.com/yourusername/ai-claims-scaleway-python.git .

# Vytvor .env súbor
nano .env

# Spusti deployment
./deploy/install.sh
```

## Architektúra

```
┌─────────────┐
│  Frontend   │ :3000 (Next.js)
│  (Next.js)  │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Backend   │ :8000 (FastAPI)
│  (FastAPI)  │
└──────┬──────┘
       │
       ├─→ PostgreSQL (Scaleway Managed)
       ├─→ S3 Storage (Scaleway Object Storage)
       └─→ Redis :6379
           │
           ↓
       ┌────────┐
       │ Worker │ (Celery)
       │        │
       └───┬────┘
           │
           ├─→ Presidio API :8001
           ├─→ Mistral/Gemini AI API
           └─→ PostgreSQL
```

## Workflow Pipeline

1. **Upload** → Nahranie PDF dokumentov
2. **OCR** → Extrakcia textu pomocou Mistral OCR
3. **Cleaning** → Čistenie a normalizácia textu
4. **Anonymization** → Anonymizácia PII pomocou Presidio
5. **Analysis** → AI analýza pomocou Mistral + RAG
6. **Report** → Generovanie PDF reportu

## Environment Variables

```env
# Mistral AI
MISTRAL_API_KEY=sk-...

# Scaleway S3
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET_NAME=ai-claims-docs
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://redis:6379/0

# Presidio
PRESIDIO_URL=http://presidio:8001
```

## Ďalšie Zdroje

- [README.md](README.md) - Hlavná dokumentácia
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - Užívateľská príručka
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technická architektúra
- [deploy/README.md](deploy/README.md) - Deployment návod

## Support

- GitHub Issues: https://github.com/yourusername/ai-claims-scaleway-python/issues
- Documentation: `/docs`


