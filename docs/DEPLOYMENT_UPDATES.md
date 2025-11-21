# 🚀 Deployment & Updates Guide

Návod na nasadzovanie nových zmien do produkčného prostredia na Scaleway.

---

## 📋 Obsah

1. [Pred Deployment](#pred-deployment)
2. [Pripojenie na Production Server](#pripojenie-na-production-server)
3. [Deployment Nových Zmien](#deployment-nových-zmien)
4. [Rollback](#rollback)
5. [Monitoring po Deployment](#monitoring-po-deployment)
6. [Troubleshooting](#troubleshooting)

---

## ✅ Pred Deployment

### Checklist

- [ ] Všetky zmeny **otestované lokálne**
- [ ] Zmeny **commitnuté** a **pushnuté** do `main` branchu na GitHube
- [ ] **Backup** production databázy (ak robíš DB zmeny)
- [ ] **Oznámenie** užívateľom (ak bude downtime)
- [ ] **Poznámky** o zmenách pripravené

### Production Info

**Server:**
- IP: `163.172.185.141`
- Hostname: `scw-ai-claims-python`
- Instance Type: DEV1-L (8 GB RAM, 4 vCPU)
- Umiestnenie: `/opt/ai-claims`

**Services:**
- Frontend: `http://163.172.185.141:8501`
- Backend API: `http://163.172.185.141:8000`
- Presidio API: `http://163.172.185.141:8001` (internal)

---

## 🔐 Pripojenie na Production Server

### SSH Pripojenie

```bash
ssh root@163.172.185.141
```

**Ak SSH nefunguje:**

1. **Scaleway Console → Serial Console**:
   - Otvor https://console.scaleway.com/instance/servers
   - Klikni na server → tab "Console" → "Open web console"
   - Login: `root`, Password: (SSH passphrase)

2. **Skontroluj Security Group**:
   - Server → Security Group → Rules
   - Port 22 musí byť otvorený

### Po Prihlásení

```bash
# Choď do app directory
cd /opt/ai-claims

# Over Git status
git status
git remote -v

# Over Docker služby
docker compose ps
```

---

## 🚀 Deployment Nových Zmien

### Automatický Update (Odporúčané)

```bash
cd /opt/ai-claims

# Spusti update script
./deploy/update.sh
```

Tento script:
1. Pull najnovšie zmeny z Gitu
2. Pull/build Docker images
3. Reštartuje služby
4. Vypíše status

---

### Manuálny Update (Krok-za-krokom)

#### 1. Pull Zmeny z Gitu

```bash
cd /opt/ai-claims
git pull origin main
```

#### 2. Build Docker Images (ak sú zmeny v kóde)

```bash
# Build všetko
docker compose build

# Alebo len špecifické služby
docker compose build backend
docker compose build worker
docker compose build frontend
docker compose build presidio
```

#### 3. Reštartuj Služby

```bash
# Reštart všetkých služieb
docker compose down
docker compose up -d

# Alebo len špecifické služby
docker compose restart backend
docker compose restart worker
docker compose restart frontend
docker compose restart presidio
```

#### 4. Over Status

```bash
# Status kontajnerov
docker compose ps

# Health checks
curl http://localhost:8001/health  # Presidio
curl http://localhost:8000/claims/  # Backend

# Logy
docker compose logs -f --tail=50
```

---

### Update Špecifických Komponentov

#### Backend API Zmeny

```bash
cd /opt/ai-claims
git pull origin main
docker compose build backend
docker compose restart backend

# Sleduj logy
docker compose logs -f backend
```

#### Worker Task Zmeny

```bash
cd /opt/ai-claims
git pull origin main
docker compose build worker
docker compose restart worker

# Sleduj logy
docker compose logs -f worker
```

#### Frontend UI Zmeny

```bash
cd /opt/ai-claims
git pull origin main
docker compose build frontend
docker compose restart frontend

# Sleduj logy
docker compose logs -f frontend
```

#### Presidio Konfigurácia Zmeny

```bash
cd /opt/ai-claims
git pull origin main
docker compose restart presidio

# Test
curl -X POST http://localhost:8001/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text":"Test 901231/1234","country":"SK","language":"en"}'
```

#### Config Zmeny (settings.yaml)

```bash
cd /opt/ai-claims
git pull origin main

# Reštartuj služby ktoré používajú config
docker compose restart backend worker
```

---

### Database Migrácie

Ak sú zmeny v databázovej schéme:

#### 1. Backup Production DB (KRITICKÉ!)

```bash
# V Scaleway Console:
# Managed Databases → tvoja DB → Backups → Create backup

# Alebo cez psql dump (ak máš prístup)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. Test Migrácia Lokálne

```bash
# Najprv testuj lokálne!
# Potom na production:
```

#### 3. Spusti Migráciu na Production

```bash
cd /opt/ai-claims
docker compose exec backend python scripts/migrate_db.py
```

#### 4. Verifikuj

```bash
# Pripoj sa k DB a over zmeny
psql $DATABASE_URL

# V psql:
\dt                    # List tables
\d+ claims             # Describe table
SELECT COUNT(*) FROM claims;
\q
```

---

## ⏮️ Rollback

Ak deployment zlyhal:

### Quick Rollback

```bash
cd /opt/ai-claims

# Vráť sa na predchádzajúci commit
git log --oneline     # Nájdi hash predchádzajúceho commitu
git reset --hard <commit-hash>

# Rebuild a reštartuj
docker compose build
docker compose down
docker compose up -d

# Over status
docker compose ps
docker compose logs -f --tail=50
```

### Database Rollback

Ak migrácia zlyhala:

```bash
# Restore z backup-u v Scaleway Console
# Managed Databases → tvoja DB → Backups → Restore

# Alebo cez psql (ak máš dump)
psql $DATABASE_URL < backup_file.sql
```

---

## 📊 Monitoring po Deployment

### Immediate Checks (prvých 5 minút)

```bash
# 1. Status kontajnerov
docker compose ps
# Všetky by mali byť "Up"

# 2. Health checks
curl http://localhost:8001/health
curl http://localhost:8000/claims/

# 3. Recent logs (hľadaj errors)
docker compose logs --tail=100 | grep -i "error"

# 4. Memory usage
docker stats --no-stream

# 5. Frontend dostupnosť
curl -I http://163.172.185.141:8501
```

### Extended Monitoring (prvých 30 minút)

```bash
# Sleduj logy real-time
docker compose logs -f

# Worker processing
docker compose logs -f worker | grep -i "succeeded\|failed"

# Backend requests
docker compose logs -f backend | grep "HTTP"

# Presidio anonymization
docker compose logs -f presidio | tail -20
```

### Manual Smoke Test

1. **Otvor Frontend**: `http://163.172.185.141:8501`
2. **Upload testovací PDF**
3. **Skontroluj OCR Review** (5-10 sekúnd)
4. **Schváľ OCR**
5. **Skontroluj Anonymization Review** (5-10 sekúnd)
6. **Schváľ Anonymizáciu**
7. **Spusti AI Analýzu**
8. **Stiahni Report**

Ak všetko funguje → ✅ Deployment úspešný!

---

## 🛑 Troubleshooting

### Service Nereštartuje

```bash
# Skontroluj logy pre error
docker compose logs <service-name>

# Force reštart
docker compose stop <service-name>
docker compose rm -f <service-name>
docker compose up -d <service-name>

# Ak nič nepomáha - rebuild
docker compose build --no-cache <service-name>
docker compose up -d <service-name>
```

### Out of Memory Errors

```bash
# Skontroluj memory usage
free -h
docker stats

# Reštartuj služby postupne
docker compose restart redis
sleep 5
docker compose restart presidio
sleep 5
docker compose restart backend worker frontend
```

### Presidio Connection Failed

```bash
# Reštartuj worker + presidio spolu
docker compose restart presidio worker

# Over health
curl http://localhost:8001/health

# Test anonymization
curl -X POST http://localhost:8001/anonymize \
  -H "Content-Type: application/json" \
  -d '{"text":"Test","country":"SK","language":"en"}'
```

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Skontroluj .env
cat .env | grep DATABASE_URL

# Reštartuj backend + worker
docker compose restart backend worker
```

### Frontend Nedostupný

```bash
# Skontroluj či beží
docker compose ps frontend

# Logy
docker compose logs frontend

# Reštart
docker compose restart frontend

# Test
curl -I http://localhost:8501
```

### Disk Full

```bash
# Skontroluj miesto
df -h

# Vyčisti Docker
docker system prune -af --volumes

# Vyčisti logy
truncate -s 0 /var/log/*.log
```

---

## 📝 Deployment Checklist

```bash
# Pre-deployment
[ ] Lokálne otestované
[ ] Commitnuté a pushnuté
[ ] Backup DB (ak potrebné)

# Deployment
[ ] SSH pripojenie
[ ] cd /opt/ai-claims
[ ] git pull origin main
[ ] docker compose build (ak potrebné)
[ ] docker compose restart (alebo ./deploy/update.sh)

# Post-deployment
[ ] docker compose ps - všetko Up
[ ] Health checks pass
[ ] Logy bez critical errors
[ ] Manual smoke test
[ ] Monitor 30 minút

# Ak zlyháva
[ ] Rollback
[ ] Check logs
[ ] Fix issue
[ ] Re-deploy
```

---

## 🔔 Poznámky

### Environment Variables

Ak pridáš novú env variable:

1. **Uprav `.env.example`** v Git repo
2. **Uprav production `.env`** na serveri:
   ```bash
   nano /opt/ai-claims/.env
   # Pridaj novú premennú
   # Ctrl+X, Y, Enter
   ```
3. **Reštartuj služby**:
   ```bash
   docker compose restart
   ```

### Security Updates

```bash
# System updates (občas)
apt-get update && apt-get upgrade -y

# Docker updates (občas)
docker compose pull
docker compose up -d
```

### Backup Strategy

- **Database**: Automatické Scaleway backups (denné)
- **Code**: Git repository
- **Config**: `.env` a `settings.yaml` zazálohované v `/root/`
  ```bash
  cp /opt/ai-claims/.env /root/.env.backup
  cp /opt/ai-claims/config/settings.yaml /root/settings.yaml.backup
  ```

---

## 📞 Emergency Contacts

Ak niečo ide zle:

1. **Rollback** na predchádzajúcu verziu (git reset)
2. **Skontroluj logy** pre root cause
3. **Serial Console** ak SSH nefunguje
4. **Reštartuj server** v Scaleway Console (last resort)

---

## 🎯 Quick Commands

```bash
# Update všetkého
cd /opt/ai-claims && ./deploy/update.sh

# Status
docker compose ps

# Logs
docker compose logs -f --tail=50

# Health
curl http://localhost:8001/health && curl http://localhost:8000/claims/

# Reštart všetkého
docker compose restart

# Full rebuild
docker compose down && docker compose build --no-cache && docker compose up -d
```

---

**Vždy testuj lokálne pred production deployment!** 🚀

