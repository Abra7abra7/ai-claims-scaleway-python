# 🌐 AI Claims - Prehľad Služieb a Prístupov

## 📋 Rýchly Prehľad

| Služba | Lokálna URL | Produkčná URL | Účel |
|--------|-------------|---------------|------|
| **Frontend** | http://localhost:3000 | https://ai-claims.novis.eu | Web aplikácia |
| **Backend API** | http://localhost:8000 | https://ai-claims.novis.eu/api | REST API |
| **API Dokumentácia** | http://localhost:8000/api/v1/docs | - | Swagger UI |
| **pgAdmin** | http://localhost:5050 | http://server-ip:5050 | Database UI |
| **MinIO Console** | http://localhost:9001 | http://server-ip:9001 | File Storage UI |
| **Redis** | localhost:6379 | localhost:6379 | Cache (CLI only) |

---

## 🖥️ LOKÁLNY VÝVOJ

### Frontend (Next.js)
```
URL:      http://localhost:3000
```

### Backend API
```
URL:      http://localhost:8000
Swagger:  http://localhost:8000/api/v1/docs
ReDoc:    http://localhost:8000/api/v1/redoc
```

### pgAdmin (Database UI)
```
URL:      http://localhost:5050
Email:    admin@admin.com
Password: admin123
```

**Pripojenie k databáze v pgAdmin:**
```
Host:     db
Port:     5432
Database: claims_db
Username: claims_user
Password: claims_password
```

### MinIO (File Storage UI)
```
URL:      http://localhost:9001
Username: minioadmin
Password: minioadmin123
Bucket:   ai-claims
```

### PostgreSQL (Direct Connection)
```
Host:     localhost
Port:     5432
Database: claims_db
Username: claims_user
Password: claims_password

Connection String:
postgresql://claims_user:claims_password@localhost:5432/claims_db
```

### Redis
```
Host:     localhost
Port:     6379
URL:      redis://localhost:6379/0
```

### Presidio (PII Anonymization API)
```
URL:      http://localhost:8001
Health:   http://localhost:8001/health
```

---

## 🌍 PRODUKCIA

### Frontend
```
URL:      https://ai-claims.novis.eu
```

### Backend API
```
URL:      https://ai-claims.novis.eu (cez reverse proxy)
Internal: http://localhost:8000
```

### pgAdmin
```
URL:      http://[server-ip]:5050
Email:    admin@admin.com
Password: admin123

⚠️ BEZPEČNOSŤ: V produkcii zmeň heslo alebo obmedz prístup firewallom!
```

### MinIO
```
URL:      http://[server-ip]:9001
Username: minioadmin
Password: minioadmin123

⚠️ BEZPEČNOSŤ: V produkcii zmeň heslo!
```

### PostgreSQL
```
Host:     localhost (len z Docker network)
Port:     5432
Database: claims_db
Username: claims_user
Password: claims_password

⚠️ BEZPEČNOSŤ: V produkcii zmeň heslo!
```

---

## 🔐 PRIHLASOVACIE ÚDAJE - ZHRNUTIE

### Default Credentials (Development)

| Služba | Username/Email | Password |
|--------|----------------|----------|
| **pgAdmin** | admin@admin.com | admin123 |
| **MinIO** | minioadmin | minioadmin123 |
| **PostgreSQL** | claims_user | claims_password |

### Aplikácia (Users)

| Role | Vytvorenie |
|------|-----------|
| **user** | Registrácia cez /auth/sign-up |
| **admin** | SQL: `UPDATE "user" SET role = 'admin' WHERE email = '...'` |

---

## 🛠️ PRIPOJENIE CEZ DESKTOP APLIKÁCIE

### DBeaver / TablePlus / DataGrip
```
Driver:   PostgreSQL
Host:     localhost
Port:     5432
Database: claims_db
Username: claims_user
Password: claims_password
```

### S3 Client (pre MinIO)
```
Endpoint: http://localhost:9000
Access Key: minioadmin
Secret Key: minioadmin123
Bucket: ai-claims
Region: us-east-1
```

---

## 📡 API ENDPOINTY

### Hlavné API Routes
```
GET  /api/v1/claims              - Zoznam claims
POST /api/v1/claims              - Vytvorenie claim
GET  /api/v1/claims/{id}         - Detail claim
DELETE /api/v1/claims/{id}       - Vymazanie claim

POST /api/v1/documents/upload    - Upload dokumentu
GET  /api/v1/documents/{id}      - Download dokumentu

GET  /api/v1/reports             - Zoznam reportov
POST /api/v1/reports/generate    - Generovanie reportu

GET  /api/v1/rag/documents       - RAG dokumenty
POST /api/v1/rag/documents       - Upload RAG dokumentu

GET  /api/v1/audit               - Audit logy
GET  /api/v1/audit/claims/{id}   - Audit pre konkrétny claim
```

### Auth API Routes (Better Auth)
```
POST /api/auth/sign-up           - Registrácia
POST /api/auth/sign-in           - Prihlásenie
POST /api/auth/sign-out          - Odhlásenie
GET  /api/auth/session           - Aktuálna session
POST /api/auth/forgot-password   - Reset hesla
POST /api/auth/reset-password    - Nové heslo
```

---

## 🚀 QUICK START

### Spustenie lokálne
```bash
# Windows
.\start-local.ps1

# Linux/Mac
make local
```

### Prístup ku službám
1. **Frontend:** http://localhost:3000
2. **API Docs:** http://localhost:8000/api/v1/docs
3. **pgAdmin:** http://localhost:5050
4. **MinIO:** http://localhost:9001

---

## ⚠️ BEZPEČNOSTNÉ ODPORÚČANIA PRE PRODUKCIU

1. **Zmeniť všetky default heslá**
2. **Obmedziť porty firewallom** (5050, 9001 len interné)
3. **Použiť silné BETTER_AUTH_SECRET**
4. **Nastaviť HTTPS** (nginx/caddy reverse proxy)
5. **Pravidelné zálohy** databázy

---

## 📁 DOCKER VOLUMES (Perzistentné Dáta)

| Volume | Služba | Čo obsahuje |
|--------|--------|-------------|
| `postgres_data` | PostgreSQL | Všetky databázové dáta |
| `minio_data` | MinIO | Uploadnuté súbory |
| `pgadmin_data` | pgAdmin | Nastavenia pgAdmin |

**Záloha:**
```bash
# Databáza
docker compose exec db pg_dump -U claims_user claims_db > backup.sql

# MinIO (skopírovať volume)
docker run --rm -v ai-claims-scaleway-python_minio_data:/data -v $(pwd):/backup alpine tar czf /backup/minio-backup.tar.gz /data
```

