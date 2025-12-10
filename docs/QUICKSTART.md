# AI Claims - Quick Start Guide

Kompletny navod pre lokalny vyvoj, production deployment a troubleshooting.

**Aktualizovane:** December 2024

---

## Obsah

1. [Lokalny Vyvoj](#1-lokalny-vyvoj)
2. [Production Deployment](#2-production-deployment)
3. [URL Adresy a Credentials](#3-url-adresy-a-credentials)
4. [Development Workflow](#4-development-workflow)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Lokalny Vyvoj

### Poziadavky

- Docker + Docker Compose (Docker Desktop pre Windows/Mac)
- Git
- Node.js 20+ (pre frontend vyvoj)

### Windows (PowerShell)

```powershell
# 1. Clone repository
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 2. Vytvor .env subor
Copy-Item .env.example .env.local
notepad .env.local   # Vyplň: MISTRAL_API_KEY, SMTP_*

# 3. Spusti
.\start-local.ps1
```

### Linux / Mac (Makefile)

```bash
# 1. Clone repository
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 2. Vytvor .env subor
cp .env.example .env.local
nano .env.local   # Vyplň: MISTRAL_API_KEY, SMTP_*

# 3. Spusti
make local
```

### Overenie ze vsetko bezi

```bash
# Status kontajnerov
docker compose ps

# Health checks
curl http://localhost:8000/api/v1/health   # Backend
curl http://localhost:3000                  # Frontend
```

**Hotovo!** Otvor http://localhost:3000

---

## 2. Production Deployment

### Server Info

- **Server:** 10.85.55.26 (IBM infrastruktura v Novis)
- **URL:** https://ai-claims.novis.eu
- **SSH:** `ssh user@10.85.55.26` alebo PuTTY

### Prvotne nasadenie

```bash
# 1. SSH na server
ssh user@10.85.55.26

# 2. Clone repo
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python

# 3. Vytvor .env
cp .env.example .env
nano .env   # Nastav produkcne hodnoty (viď nižšie)

# 4. Spusti
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Over status
docker-compose ps
```

### Update existujuceho nasadenia

```bash
# 1. SSH na server
ssh user@10.85.55.26
cd ~/ai-claims-scaleway-python

# 2. Pull zmeny
git pull origin main

# 3. Rebuild a restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Nginx konfiguracia

Subor: `/etc/nginx/sites-enabled/ai-claims`

```nginx
server {
    listen 443 ssl;
    server_name ai-claims.novis.eu;

    client_max_body_size 200M;
    
    ssl_certificate /etc/nginx/certificates/fullchain.crt;
    ssl_certificate_key /etc/nginx/certificates/privkey.key;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API (FastAPI)
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Po zmene nginx:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 3. URL Adresy a Credentials

### Lokalne URL

| Sluzba | URL | Credentials |
|--------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000 | - |
| **Swagger Docs** | http://localhost:8000/api/v1/docs | - |
| **pgAdmin** | http://localhost:5050 | admin@admin.com / admin123 |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 |

### Produkcne URL

| Sluzba | URL |
|--------|-----|
| **Frontend** | https://ai-claims.novis.eu |
| **Backend API** | https://ai-claims.novis.eu/api/v1 |
| **pgAdmin** | http://[server-ip]:5050 |
| **MinIO Console** | http://[server-ip]:9001 |

### Database Credentials

```
Host:     localhost (alebo 'db' z Docker)
Port:     5432
Database: claims_db
Username: claims_user
Password: claims_password
```

**Connection string:**
```
postgresql://claims_user:claims_password@localhost:5432/claims_db
```

### Environment Variables

Minimalny `.env` pre lokalny vyvoj:

```env
# AI Provider (GDPR compliant)
MISTRAL_API_KEY=your-mistral-key
LLM_PROVIDER=mistral

# Email (SMTP) - POVINNE pre registraciu!
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tvoj@gmail.com
SMTP_PASSWORD=app-password-nie-bezne-heslo
SMTP_FROM=noreply@company.com
SMTP_USE_TLS=true
FRONTEND_URL=http://localhost:3000
```

Dodatocne pre produkciu:

```env
ENVIRONMENT=production
FRONTEND_URL=https://ai-claims.novis.eu
NEXT_PUBLIC_API_URL=https://ai-claims.novis.eu
NEXT_PUBLIC_APP_URL=https://ai-claims.novis.eu
BETTER_AUTH_SECRET=min-32-znakov-nahodny-string
```

---

## 4. Development Workflow

### Git Workflow

```bash
# 1. Vytvor feature branch
git checkout main
git pull
git checkout -b feature/moja-funkcia

# 2. Urob zmeny a commitni
git add .
git commit -m "feat: pridana nova funkcia"

# 3. Push
git push origin feature/moja-funkcia

# 4. Po merge
git checkout main
git pull
git branch -d feature/moja-funkcia
```

### Commit Messages (Conventional Commits)

```
feat: pridana email verifikacia
fix: opraveny CORS error
docs: aktualizovany README
refactor: zlepseny OCR service
```

### Automaticka generacia TypeScript typov

Pri kazdom `git commit` sa automaticky:
1. Skontroluje ci backend bezi
2. Vygeneruju TypeScript typy z OpenAPI
3. Pridaju sa do commitu

**Ak backend nebezi:**
```bash
docker compose up -d backend
```

**Manualna generacia:**
```bash
cd frontend
npm run generate-types
```

### Pridanie noveho API Endpointu

1. Vytvor schema v `app/api/v1/schemas/`
2. Vytvor endpoint v `app/api/v1/endpoints/`
3. Registruj v `app/api/v1/router.py`
4. Restartuj: `docker compose restart backend`
5. Typy sa vygeneruju automaticky pri commite

### Pridanie novej Frontend stranky

1. Vytvor `frontend/src/app/moja-stranka/page.tsx`
2. Pridaj preklady do `frontend/src/messages/sk.json` a `en.json`
3. Pridaj do sidebar menu v `frontend/src/components/layout/sidebar.tsx`

---

## 5. Troubleshooting

### NEXT_PUBLIC_* problem (localhost:8000 v produkcii)

**Problem:** Frontend v produkcii vola localhost:8000

**Pricina:** NEXT_PUBLIC_* premenne sa "zapekaju" pocas buildu

**Riesenie:**
```bash
# Force rebuild bez cache
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend
```

### Nginx 502 Bad Gateway

**Pricina:** Kontajnery nebezia

**Riesenie:**
```bash
docker-compose ps                    # Skontroluj status
docker-compose up -d                 # Spusti kontajnery
docker-compose logs frontend         # Pozri logy
```

### Nginx 404 Not Found na /api

**Pricina:** Zla nginx konfiguracia (dvojite lomitko)

**Riesenie:** Skontroluj nginx config:
```nginx
# SPRAVNE:
location /api {
    proxy_pass http://localhost:8000;    # BEZ trailing slash!
}

# ZLE:
location /api/ {
    proxy_pass http://localhost:8000/api/;   # Sposobi /api//v1/...
}
```

### Email sa neposiela

**Kontrola:**
```bash
docker-compose logs backend | grep -i email
docker-compose logs backend | grep -i smtp
```

**Caste priciny:**
- Gmail: Potrebujes **App Password** (nie bezne heslo)
- Zle credentials v `.env`
- Port 587 blokovany firewallom

### Worker task zaseknuty

```bash
# Restart worker
docker-compose restart worker

# Pozri Redis queue
docker-compose exec redis redis-cli LLEN celery
```

### Database connection error

```bash
# Over ze db bezi
docker-compose ps db

# Restart db
docker-compose restart db

# Pripoj sa manualne
docker-compose exec db psql -U claims_user -d claims_db
```

### Cistenie Docker cache

```bash
# Zastav vsetko
docker-compose down

# Vymaz images a volumes (POZOR: zmaze data!)
docker system prune -a --volumes -f

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

---

## Uzitocne prikazy

```bash
# Logy
docker-compose logs -f              # Vsetky
docker-compose logs -f backend      # Len backend
docker-compose logs --tail 50 worker

# Status
docker-compose ps

# Restart
docker-compose restart backend
docker-compose restart frontend

# Shell v kontajneri
docker-compose exec backend bash
docker-compose exec db psql -U claims_user -d claims_db

# Databaza backup
docker-compose exec db pg_dump -U claims_user claims_db > backup.sql
```

---

## Dalsie zdroje

- **[HANDOVER.md](HANDOVER.md)** - Historia projektu, architekturne rozhodnutia
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailna technicka dokumentacia

---

**Posledna aktualizacia:** December 2024

