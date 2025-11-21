# 🛠️ Development Guide - AI Claims System

Tento návod ti ukáže ako pracovať na projekte lokálne, testovať zmeny a pripravovať ich na deployment.

---

## 📋 Obsah

1. [Setup Lokálneho Vývojového Prostredia](#setup-lokálneho-vývojového-prostredia)
2. [Štruktúra Projektu](#štruktúra-projektu)
3. [Workflow pre Vývoj](#workflow-pre-vývoj)
4. [Testovanie](#testovanie)
5. [Debugging](#debugging)
6. [Best Practices](#best-practices)

---

## 🚀 Setup Lokálneho Vývojového Prostredia

### Požiadavky

- **Docker Desktop** (pre Mac/Windows) alebo **Docker Engine** (Linux)
- **Git**
- **Python 3.11+** (voliteľné, pre lokálny development bez Dockeru)
- **IDE**: VS Code, PyCharm, alebo Cursor

### 1. Clone Repository

```bash
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python
```

### 2. Vytvor `.env` Súbor

```bash
cp .env.example .env
```

Vyplň potrebné credentials v `.env`:

```env
# Mistral AI
MISTRAL_API_KEY=sk-...  # Tvoj Mistral API key

# Scaleway S3 (production credentials alebo test bucket)
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET_NAME=ai-claims-docs-dev  # Použi dev bucket!
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

# Database (môžeš použiť lokálny PostgreSQL alebo Scaleway dev DB)
DATABASE_URL=postgresql://user:pass@host:port/db_dev

# Redis (internal Docker)
REDIS_URL=redis://redis:6379/0

# Presidio (internal Docker)
PRESIDIO_URL=http://presidio:8001
```

**Dôležité:**
- Použi **DEV/TEST credentials**, nie production!
- Pre lokálny DB môžeš použiť lokálny PostgreSQL alebo Docker

### 3. Spusti Služby

```bash
# Jednoduchý startup
./local-start.sh

# Alebo manuálne
docker compose build
docker compose up -d

# Sleduj logy
docker compose logs -f
```

### 4. Over Že Všetko Beží

```bash
# Kontajnery
docker compose ps

# Health checks
curl http://localhost:8001/health  # Presidio
curl http://localhost:8000/claims/  # Backend

# Frontend
open http://localhost:8501
```

---

## 📁 Štruktúra Projektu

```
ai-claims-scaleway-python/
├── app/                        # Backend aplikácia
│   ├── core/
│   │   ├── config.py          # Pydantic settings (env variables)
│   │   └── config_loader.py   # YAML config loader
│   ├── db/
│   │   ├── models.py          # SQLAlchemy modely (Claim, Document, atď.)
│   │   └── session.py         # Database session
│   ├── services/              # Business logic
│   │   ├── storage.py         # S3 operations
│   │   ├── ocr.py             # Mistral OCR
│   │   ├── cleaner.py         # Text cleaning
│   │   ├── mistral.py         # Mistral AI client
│   │   ├── rag.py             # RAG system
│   │   ├── report_generator.py # PDF generation
│   │   ├── audit.py           # Audit logging
│   │   └── anonymizer.py      # (legacy, now uses Presidio API)
│   ├── api/                   # API endpoints (ak existuje)
│   ├── main.py                # FastAPI app (routes)
│   ├── worker.py              # Celery tasks
│   └── prompts.py             # (deprecated - now in config/settings.yaml)
│
├── frontend/
│   └── app.py                 # Streamlit UI
│
├── presidio-api/              # Samostatná Presidio služba
│   ├── app.py                 # FastAPI wrapper pre Presidio
│   ├── requirements.txt
│   └── Dockerfile
│
├── config/
│   └── settings.yaml          # Centrálna konfigurácia
│                              # (prompts, LLM settings, Presidio config)
│
├── scripts/
│   ├── migrate_db.py          # Database migrations
│   └── verify_connections.py # Test connections
│
├── deploy/                    # Deployment skripty
│   ├── setup.sh              # Server setup
│   ├── install.sh            # App deployment
│   ├── update.sh             # Update script
│   └── README.md             # Deployment guide
│
├── docs/                      # Dokumentácia
│   ├── DEVELOPMENT.md         # Tento súbor
│   └── DEPLOYMENT_UPDATES.md  # Deployment guide
│
├── docker-compose.yml         # Development config
├── docker-compose.prod.yml    # Production overrides
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt           # Python dependencies
├── .env.example               # Template pre .env
├── .gitignore
├── Makefile                   # Helper commands
├── local-start.sh            # Local startup script
└── README.md
```

---

## 🔄 Workflow pre Vývoj

### Typický Development Cycle

```bash
# 1. Vytvor nový branch
git checkout -b feature/moja-nova-funkcia

# 2. Uprav kód
# Edituj súbory v app/, frontend/, config/, atď.

# 3. Reštartuj príslušné služby
docker compose restart backend    # Ak si menil backend
docker compose restart worker     # Ak si menil worker tasks
docker compose restart frontend   # Ak si menil frontend

# 4. Testuj zmeny
# Otvor http://localhost:8501 a testuj manuálne

# 5. Sleduj logy
docker compose logs -f backend
docker compose logs -f worker

# 6. Commit zmeny
git add .
git commit -m "feat: pridaná nová funkcia XYZ"

# 7. Push do remote
git push origin feature/moja-nova-funkcia
```

### Kde Robiť Zmeny

#### 1. **Backend API Endpoints** (`app/main.py`)

Pridanie nového endpointu:

```python
@app.post("/my-new-endpoint")
async def my_new_endpoint(data: MyModel):
    # Your logic here
    return {"status": "ok"}
```

Po zmene:
```bash
docker compose restart backend
```

#### 2. **Celery Worker Tasks** (`app/worker.py`)

Pridanie novej async úlohy:

```python
@celery_app.task(name="app.worker.my_new_task")
def my_new_task(param1: str):
    # Your logic here
    return f"Task completed: {param1}"
```

Po zmene:
```bash
docker compose restart worker
```

#### 3. **Frontend UI** (`frontend/app.py`)

Pridanie novej stránky:

```python
def my_new_page():
    st.title("Moja Nová Stránka")
    # Your Streamlit code here

# V main()
pages = {
    "Moja Stránka": my_new_page,
    # ... existing pages
}
```

Po zmene:
```bash
docker compose restart frontend
```

#### 4. **Database Models** (`app/db/models.py`)

Pridanie nového stĺpca alebo tabuľky:

```python
class MyNewModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)
```

Po zmene:
```bash
# Uprav scripts/migrate_db.py
# Spusti migráciu
docker compose exec backend python scripts/migrate_db.py
```

#### 5. **Konfigurácia** (`config/settings.yaml`)

Zmeny v LLM nastaveniach, promptoch, Presidio config:

```yaml
llm:
  analysis_model: mistral-large-latest  # Upgrade modelu

prompts:
  my_new_prompt:
    name: "Môj Nový Prompt"
    template: |
      Your prompt here...
```

Po zmene:
```bash
docker compose restart backend worker
```

---

## 🧪 Testovanie

### Manuálne Testovanie

1. **Upload dokumentu** cez Frontend
2. **Sleduj logy** worker-a:
   ```bash
   docker compose logs -f worker
   ```
3. **Skontroluj OCR Review** stránku
4. **Schváľ OCR** a sleduj cleaning + anonymizáciu
5. **Skontroluj Anonymization Review**
6. **Schváľ anonymizáciu** a spusti AI analýzu
7. **Stiahni report**

### API Testovanie

```bash
# Test upload
curl -X POST http://localhost:8000/upload/ \
  -F "files=@test.pdf" \
  -F "country=SK"

# Test health endpoints
curl http://localhost:8000/claims/
curl http://localhost:8001/health

# Test Presidio anonymization
curl -X POST http://localhost:8001/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ján Novák 901231/1234",
    "country": "SK",
    "language": "en"
  }'
```

### Unit Testy (TODO)

```bash
# Budúce rozšírenie
pytest tests/
```

---

## 🐛 Debugging

### Logs

```bash
# Všetky služby
docker compose logs -f

# Špecifická služba
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f presidio
docker compose logs -f frontend

# Posledných N riadkov
docker compose logs --tail=50 worker

# Grep pre errors
docker compose logs worker | grep -i "error"
```

### Pripojenie do Kontajnera

```bash
# Backend shell
docker compose exec backend bash

# Worker shell
docker compose exec worker bash

# Spusti Python v kontajneri
docker compose exec backend python
>>> from app.db.session import SessionLocal
>>> db = SessionLocal()
>>> # Testuj databázové queries
```

### Database Debugging

```bash
# Pripoj sa k PostgreSQL
psql $DATABASE_URL

# V psql
\dt                          # List tables
SELECT * FROM claims LIMIT 5;
SELECT * FROM claim_documents WHERE claim_id = 1;
\q
```

### Health Checks

```bash
# Makefile command
make health

# Alebo manuálne
curl http://localhost:8000/claims/
curl http://localhost:8001/health
docker compose exec redis redis-cli ping
```

---

## ✅ Best Practices

### Git Workflow

1. **Vždy vytvor nový branch** pre novú feature
2. **Používaj descriptive commit messages**:
   - `feat: pridaná nová funkcia`
   - `fix: opravená chyba v anonymizácii`
   - `docs: aktualizovaná dokumentácia`
3. **Commit často** (malé atomic commits)
4. **Push do remote** pravidelne

### Code Style

- **Python**: Dodržuj PEP 8
- **Docstrings**: Dokumentuj funkcie a classy
- **Type Hints**: Použi type hints kde je to možné
- **Comments**: Píš komentáre pre zložitú logiku

### Environment Variables

- **Nikdy** necommituj `.env` súbor!
- **Vždy** používaj `.env.example` ako template
- **Test credentials**: Použi DEV credentials, nie production

### Docker

- **Reštartuj služby** po zmenách kódu
- **Build cache**: Použi `--no-cache` ak máš problémy:
  ```bash
  docker compose build --no-cache backend
  ```
- **Vyčisti resources**: 
  ```bash
  docker system prune -af
  ```

### Database

- **Nikdy** nemazuj production dáta!
- **Backup** pred veľkými zmenami v schéme
- **Migrácie**: Vždy testuj najprv lokálne

---

## 🚢 Priprava na Deployment

Pred nasadením na production:

1. **Testuj lokálne** všetky zmeny
2. **Commit a push** do `main` branchu
3. **Sleduj** [DEPLOYMENT_UPDATES.md](DEPLOYMENT_UPDATES.md) pre deployment steps
4. **Backup** production databázy (ak robíš DB zmeny)
5. **Deploy** na staging (ak máš) pred production

---

## 📞 Pomoc

- **Logy**: Vždy najprv skontroluj logy
- **Documentation**: Pozri ostatné `.md` súbory
- **Issues**: Otvor issue na GitHube ak niečo nejde

---

**Happy coding! 🎉**

