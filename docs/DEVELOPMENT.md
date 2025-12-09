# 🛠️ Development Guide - AI Claims System

**Last Updated:** December 9, 2024

Kompletný návod pre vývoj, testovanie a deployment prípravu nových features.

---

## 📋 Obsah

1. [Setup Lokálneho Prostredia](#setup-lokálneho-prostredia)
2. [Development Workflow](#development-workflow)
3. [Pridanie Nového Endpointu](#pridanie-nového-endpointu)
4. [Pridanie Novej Frontend Stránky](#pridanie-novej-frontend-stránky)
5. [Type Generation](#type-generation)
6. [Testing](#testing)
7. [Debugging](#debugging)
8. [Git Workflow](#git-workflow)
9. [Best Practices](#best-practices)

---

## 🚀 Setup Lokálneho Prostredia

### Požiadavky

- **Docker + Docker Compose** (Docker Desktop pre Mac/Windows)
- **Git**
- **Node.js 20+** (pre frontend development)
- **Python 3.11+** (voliteľné, pre backend development bez Dockeru)
- **IDE**: VS Code, Cursor, alebo PyCharm

### Rýchly Štart (4 kroky)

```bash
# 1. Clone repository
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 2. Vytvor .env súbor
cp .env.example .env
# Vyplň: SMTP_*, MISTRAL_API_KEY alebo GEMINI_API_KEY

# 3. Spusti Docker služby
docker-compose up -d

# 4. Vytvor admin usera
docker-compose exec backend python scripts/init_admin.py
```

**Hotovo!** Otvor http://localhost:3000

### Potrebné Environment Variables

Minimálne potrebné pre lokálny vývoj:

```env
# AI Provider (aspoň jeden)
MISTRAL_API_KEY=your-key
# alebo
GEMINI_API_KEY=your-key
LLM_PROVIDER=gemini

# Email (SMTP) - POVINNÉ!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tvoj-email@gmail.com
SMTP_PASSWORD=tvoj-app-password  # Gmail App Password
SMTP_FROM=noreply@company.com
SMTP_USE_TLS=true
FRONTEND_URL=http://localhost:3000

# MinIO (lokálne S3)
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=ai-claims
S3_ENDPOINT_URL=http://minio:9000

# Database (Docker internal)
DATABASE_URL=postgresql://claims_user:claims_password@db:5432/claims_db

# Redis (Docker internal)
REDIS_URL=redis://redis:6379
```

**NIKDY necommituj `.env` do Gitu!**

### Overenie Že Všetko Beží

```bash
# Kontajnery status
docker-compose ps

# Health checks
curl http://localhost:8000/api/v1/health  # Backend
curl http://localhost:8001/health         # Presidio
curl http://localhost:3000                # Frontend

# Logy
docker-compose logs -f backend
```

---

## 🔄 Development Workflow

### Typický Development Cycle

```bash
# 1. Vytvor feature branch
git checkout -b feature/nova-funkcia

# 2. Uprav kód
# Edituj súbory v app/, frontend/src/, atď.

# 3. Reštartuj služby (ak treba)
docker-compose restart backend   # Backend zmeny
docker-compose restart worker    # Worker tasks zmeny
docker-compose restart frontend  # Frontend zmeny (ale hot reload funguje)

# 4. Testuj
# Frontend: http://localhost:3000 (auto-reload)
# Backend API: http://localhost:8000/api/v1/docs

# 5. Sleduj logy
docker-compose logs -f backend

# 6. Commit & push
git add .
git commit -m "feat: pridaná nova funkcia"
git push origin feature/nova-funkcia
```

---

## 🔌 Pridanie Nového Endpointu

### 1. Vytvor Pydantic Schema

**Súbor:** `app/api/v1/schemas/my_feature.py`

```python
from pydantic import BaseModel
from datetime import datetime

class MyFeatureRequest(BaseModel):
    name: str
    value: int

class MyFeatureResponse(BaseModel):
    id: int
    name: str
    value: int
    created_at: datetime
```

### 2. Vytvor Endpoint Handler

**Súbor:** `app/api/v1/endpoints/my_feature.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_database
from app.api.v1.schemas.my_feature import MyFeatureRequest, MyFeatureResponse

router = APIRouter()

@router.post("", response_model=MyFeatureResponse)
def create_feature(
    data: MyFeatureRequest,
    db: Session = Depends(get_database)
):
    """
    Create new feature.
    """
    # Your logic here
    return MyFeatureResponse(
        id=1,
        name=data.name,
        value=data.value,
        created_at=datetime.utcnow()
    )

@router.get("/{id}", response_model=MyFeatureResponse)
def get_feature(id: int, db: Session = Depends(get_database)):
    """
    Get feature by ID.
    """
    # Your logic here
    pass
```

### 3. Registruj v Router

**Súbor:** `app/api/v1/router.py`

```python
from app.api.v1.endpoints import my_feature  # Import

api_router = APIRouter()

# Register new router
api_router.include_router(
    my_feature.router,
    prefix="/my-feature",
    tags=["My Feature"]
)
```

### 4. Reštartuj Backend

```bash
docker-compose restart backend
```

### 5. Vygeneruj TypeScript Typy

```bash
cd frontend
npm run generate-types
```

**Hotovo!** Nový endpoint je dostupný na `/api/v1/my-feature` a typy sú vygenerované vo `frontend/src/lib/api-types.ts`.

---

## 🎨 Pridanie Novej Frontend Stránky

### 1. Vytvor Page Component

**Súbor:** `frontend/src/app/my-page/page.tsx`

```tsx
"use client";

import { useTranslations } from "next-intl";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function MyPage() {
  const t = useTranslations("myPage");

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-3xl font-bold mb-6">{t("title")}</h1>
      
      <Card className="p-6">
        <p>{t("description")}</p>
        <Button className="mt-4">{t("action")}</Button>
      </Card>
    </div>
  );
}
```

### 2. Pridaj Preklady

**Súbor:** `frontend/src/messages/sk.json`

```json
{
  "myPage": {
    "title": "Moja Stránka",
    "description": "Toto je moja nová stránka.",
    "action": "Vykonaj akciu"
  }
}
```

**Súbor:** `frontend/src/messages/en.json`

```json
{
  "myPage": {
    "title": "My Page",
    "description": "This is my new page.",
    "action": "Perform Action"
  }
}
```

### 3. Pridaj do Sidebar Menu

**Súbor:** `frontend/src/components/layout/sidebar.tsx`

```tsx
const navItems = [
  // ... existing items ...
  {
    href: "/my-page",
    label: t("nav.myPage"),
    icon: IconName,
  },
];
```

### 4. Testuj

Otvor http://localhost:3000/my-page - Next.js hot reload automaticky načíta novú stránku!

---

## 🔄 Type Generation

### Automatická Generácia

TypeScript typy sa generujú automaticky pri `git commit` pomocou **pre-commit hook**.

**Ako to funguje:**
1. Commit zmeny v `app/api/v1/schemas/*.py`
2. Git hook detekuje backend zmeny
3. Automaticky spustí `npm run generate-types` vo `frontend/`
4. Typy sa vygenerujú do `frontend/src/lib/api-types.ts`
5. Súbor sa automaticky pridá do commitu

### Manuálna Generácia

```bash
cd frontend
npm run generate-types
```

### Watch Mode (pre aktívny vývoj)

```bash
cd frontend
npm run types:watch
```

Typy sa budú automaticky regenerovať pri každej zmene v `app/` priečinku.

**Viac info:** [`docs/GIT_HOOKS.md`](GIT_HOOKS.md)

---

## 🧪 Testing

### Manuálne Testovanie

**Kompletný flow:**
1. Upload PDF dokumentu (`/claims/new`)
2. Sleduj worker logy: `docker-compose logs -f worker`
3. OCR review (`/claims/[id]/ocr`)
4. Approve OCR
5. Anonymization review (`/claims/[id]/anon`)
6. Approve anonymization
7. Start analysis (`/claims/[id]/analysis`)
8. Download report (`/reports`)

### API Testovanie (curl)

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List claims
curl http://localhost:8000/api/v1/claims \
  -H "Cookie: session_token=YOUR_TOKEN"

# Upload claim
curl -X POST http://localhost:8000/api/v1/claims \
  -F "file=@test.pdf" \
  -F "country=SK" \
  -H "Cookie: session_token=YOUR_TOKEN"
```

### Swagger UI

Otvor http://localhost:8000/api/v1/docs pre interaktívne API testovanie.

### Frontend Testing

```bash
cd frontend
npm run lint       # ESLint check
npm run build      # Production build test
```

---

## 🐛 Debugging

### Zobrazenie Logov

```bash
# Všetky služby
docker-compose logs -f

# Konkrétna služba
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Posledných 100 riadkov
docker-compose logs --tail 100 backend

# Filtrovať errors
docker-compose logs backend | grep ERROR
```

### Pripojenie do Kontajnera

```bash
# Backend shell
docker-compose exec backend bash

# Worker shell
docker-compose exec worker bash

# Python REPL v kontajneri
docker-compose exec backend python
>>> from app.db.models import User
>>> from app.db.database import SessionLocal
>>> db = SessionLocal()
>>> users = db.query(User).all()
>>> print(users)
```

### Database Debugging

```bash
# Pripoj sa k PostgreSQL
docker-compose exec db psql -U claims_user -d claims_db

# SQL queries
SELECT * FROM users;
SELECT * FROM claims ORDER BY created_at DESC LIMIT 10;
SELECT * FROM audit_logs WHERE action LIKE 'LOGIN%';
\dt  # List tables
\d users  # Describe table
\q  # Quit
```

### Časté Problémy

#### Email sa neposiela
```bash
# Over ENV variables
docker-compose exec backend python -c "from app.core.config import get_settings; s = get_settings(); print(f'SMTP: {s.SMTP_HOST}:{s.SMTP_PORT}')"

# Reštartuj s novými ENV
docker-compose down backend
docker-compose up -d backend
```

#### Worker task zaseknutý
```bash
# Zisti stav Redis queue
docker-compose exec redis redis-cli LLEN celery

# Reštartuj worker
docker-compose restart worker
```

#### Frontend 404 na novej stránke
```bash
# Next.js potrebuje reload pre nové routes
docker-compose restart frontend
```

---

## 📝 Git Workflow

### Branching Strategy

```bash
main                          # Production code
  └─ feature/nova-funkcia     # Feature development
  └─ fix/oprava-bugu          # Bug fixes
```

### Commit Messages

Používaj **Conventional Commits**:

```bash
feat: pridaná email verifikácia
fix: opravený CORS error
docs: aktualizovaný README
refactor: zlepšený OCR service
chore: update dependencies
```

### Development Cycle

```bash
# 1. Vytvor branch
git checkout main
git pull
git checkout -b feature/moja-funkcia

# 2. Vývoj a commit
git add .
git commit -m "feat: pridaná funkcia X"

# 3. Push
git push origin feature/moja-funkcia

# 4. Po merge
git checkout main
git pull
git branch -d feature/moja-funkcia
```

### Pre-Commit Hooks

Projekt má automatické hooks:
- ✅ TypeScript typy sa generujú automaticky
- ✅ Viac info: [`docs/GIT_HOOKS.md`](GIT_HOOKS.md)

---

## ✅ Best Practices

### Code Quality

**Python (Backend):**
- ✅ Type hints pre všetky funkcie
- ✅ Pydantic schemas pre validation
- ✅ Docstrings pre public API
- ✅ PEP 8 formatting

**TypeScript (Frontend):**
- ✅ Používaj auto-generated `api-types.ts`
- ✅ Strict mode enabled
- ✅ Type všetky props a state
- ✅ ESLint compliance

### Security **KRITICKÉ**

- 🔒 **NIKDY** necommituj `.env` do Gitu!
- 🔒 **NIKDY** neloguj passwords/tokens
- 🔒 Používaj DEV credentials lokálne
- 🔒 Validuj všetky inputs (Pydantic)
- 🔒 Sanitizuj SQL (SQLAlchemy ORM)

### Docker

```bash
# Hot reload je enabled (volumes mounted)
# Rebuild len ak dependencies zmenené
docker-compose build --no-cache backend

# Cleanup
docker system prune -af
docker volume prune -f
```

### Database

1. ✅ Testuj migrácie lokálne
2. ✅ Backup pred production migráciou
3. ✅ Rollback plán pripravený
4. ✅ Nikdy `DROP TABLE` v production!

### Performance

- ⚡ `react-query` cache pre API calls
- ⚡ Lazy load Next.js pages
- ⚡ Debounce search inputs
- ⚡ Index DB queries (pgvector)
- ⚡ Celery pre long-running tasks

---

## 🚀 Deployment Príprava

Pred nasadením na production:

1. ✅ **Testuj lokálne** kompletný flow
2. ✅ **Commit a push** do `main`
3. ✅ **Backup production DB** (ak DB zmeny)
4. ✅ **Sleduj deployment guide**: [`docs/PRODUCTION_DEPLOYMENT.md`](PRODUCTION_DEPLOYMENT.md)
5. ✅ **Reštartuj služby** na serveri
6. ✅ **Overil health checks** po deploye

---

## 📚 Ďalšie Zdroje

- **[`docs/HANDOVER.md`](HANDOVER.md)** - Kompletný prehľad systému
- **[`docs/ARCHITECTURE.md`](ARCHITECTURE.md)** - Technická architektúra
- **[`docs/PRODUCTION_DEPLOYMENT.md`](PRODUCTION_DEPLOYMENT.md)** - Deployment na server
- **[`docs/GIT_HOOKS.md`](GIT_HOOKS.md)** - Type generation automation

---

**Last Updated:** December 9, 2024  
**Happy coding! 🚀**
