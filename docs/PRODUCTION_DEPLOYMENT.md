# 🚀 Production Deployment Guide

## Aktualizované: 9. December 2024

---

## 📋 Čo bolo opravené

### CORS Configuration
- ✅ Zmenené z wildcard `*` na špecifické domény
- ✅ Pridaná podpora pre `credentials: 'include'` (cookies)
- ✅ Produkčná doména: `https://ai-claims.novis.eu`

### API URL Configuration  
- ✅ Frontend používa produkčnú URL namiesto `localhost`
- ✅ Nastavené cez `NEXT_PUBLIC_API_URL` v `docker-compose.prod.yml`

---

## 🚀 Deployment na Server

### Krok 1: Pripoj sa na server

```bash
ssh root@10.85.55.26
# alebo cez PuTTY
```

### Krok 2: Pull najnovšie zmeny

```bash
cd ~/ai-claims-scaleway-python
git pull
```

### Krok 3: Reštartuj služby

```bash
# Zastaviť všetko
docker-compose down

# Spustiť s produkčnou konfiguráciou
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Počkaj 30 sekúnd na štart
sleep 30

# Over status
docker-compose ps
```

### Krok 4: Vytvor admin používateľa

```bash
docker-compose exec backend python scripts/init_admin.py
```

Alebo manuálne:

```bash
docker-compose exec backend python -c "
from app.db.database import SessionLocal
from app.services.auth import AuthService
from app.db.models import UserRole

db = SessionLocal()
auth = AuthService()

user = auth.create_user(
    db=db,
    email='admin@company.sk',
    password='YourSecurePassword123',
    name='Admin User',
    role=UserRole.ADMIN
)
print(f'✅ User created: {user.email}')
db.close()
"
```

### Krok 5: Over že funguje

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Frontend logs
docker-compose logs frontend | tail -50

# Backend logs
docker-compose logs backend | tail -50
```

---

## 🌐 Prístup

| Služba | URL |
|--------|-----|
| **Frontend** | https://ai-claims.novis.eu |
| **Backend API** | https://ai-claims.novis.eu/api/v1/docs |
| **Health Check** | https://ai-claims.novis.eu/api/v1/health |

---

## ⚙️ Konfigurácia

### Environment Variables (.env na serveri)

```bash
# Database
DATABASE_URL=postgresql://claims_user:claims_password@db:5432/claims_db

# LLM Provider (Mistral - GDPR compliant)
LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_actual_mistral_api_key

# S3 Storage
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=ai-claims
S3_ENDPOINT_URL=http://minio:9000
S3_REGION=us-east-1

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ADMIN_EMAIL=admin@company.sk
ADMIN_PASSWORD=secure_password_here

# Frontend URL (pre CORS)
FRONTEND_URL=https://ai-claims.novis.eu

# Redis
REDIS_URL=redis://redis:6379/0

# Presidio
PRESIDIO_URL=http://presidio:8001
```

---

## 🔧 Riešenie problémov

### CORS Error

**Symptóm:**
```
Access to fetch has been blocked by CORS policy
```

**Riešenie:**
1. Over že `FRONTEND_URL` je nastavená v `.env`
2. Reštartuj backend: `docker-compose restart backend`

### API 404 Error

**Symptóm:**
```
Failed to load resource: net::ERR_FAILED
```

**Riešenie:**
1. Over že frontend má správnu API URL
2. Pozri logy: `docker-compose logs frontend`
3. Rebuild frontend: `docker-compose up -d --build frontend`

### Nemôžem sa prihlásiť

**Riešenie:**
1. Vytvor používateľa cez CLI (viď Krok 4 vyššie)
2. Over backend logy: `docker-compose logs backend | grep auth`
3. Skontroluj databázu:
   ```bash
   docker-compose exec db psql -U claims_user -d claims_db -c "SELECT * FROM users;"
   ```

---

## 📊 Monitoring

### Pozri logy

```bash
# Všetky služby
docker-compose logs -f

# Len frontend
docker-compose logs -f frontend

# Len backend
docker-compose logs -f backend

# Posledných 100 riadkov
docker-compose logs --tail 100 backend
```

### Status služieb

```bash
docker-compose ps
```

### Využitie zdrojov

```bash
docker stats
```

---

## 🔄 Update Workflow

### Lokálne (tvoj PC):

```powershell
# 1. Urob zmeny
# ... edit files ...

# 2. Commit (typy sa vygenerujú automaticky!)
git add .
git commit -m "Your changes"

# 3. Push
git push
```

### Na serveri:

```bash
cd ~/ai-claims-scaleway-python
git pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 🛡️ Security Checklist

- [ ] Zmenené default heslá v `.env`
- [ ] `SECRET_KEY` je unikátny a min. 32 znakov
- [ ] `MISTRAL_API_KEY` je nastavený (GDPR compliant)
- [ ] HTTPS je nakonfigurované (nginx/caddy)
- [ ] Firewall povoľuje len potrebné porty
- [ ] Database backupy sú nastavené
- [ ] Audit logy sa monitorujú

---

## 📞 Support

Pre problémy kontaktuj: admin@company.sk

