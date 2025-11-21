# Deployment Checklist - AI Claims na Scaleway

## ✅ Opravy (už hotové)

### 1. Docker Configuration
- ✅ Pridaný `presidio` do `depends_on` pre worker service
- ✅ Pridaná environment variable `PRESIDIO_URL` pre worker
- ✅ Pridaný healthcheck pre Presidio service
- ✅ Odstránený nesprávny `depends_on: backend` z Presidio (circular dependency)
- ✅ Pridaný `restart: unless-stopped` pre Presidio

### 2. Presidio Dockerfile
- ✅ Pridaný `curl` pre healthcheck
- ✅ Pridaný `spacy>=3.5.0` do requirements.txt
- ✅ Inštalácia spaCy modelu `en_core_web_lg`

### 3. Scripts & Tools
- ✅ Vytvorený `local-start.sh` - lokálne spustenie s health checks
- ✅ Aktualizovaný `Makefile` - nové príkazy (health, rebuild, etc.)
- ✅ Vytvorený `QUICK_START.md` - rýchla dokumentácia
- ✅ Deployment skripty v `deploy/` priečinku už existujú

### 4. Testovanie
- ✅ Presidio beží a je healthy
- ✅ Worker sa úspešne pripája k Presidio
- ✅ Anonymizácia funguje správne (test úspešný)

## 📋 Checklist pred Nasadením na Scaleway

### Pre-deployment Príprava

- [ ] Vytvorený Scaleway Instance (DEV1-M alebo väčší)
- [ ] Nakonfigurovaná Security Group:
  - [ ] Port 22 (SSH) - len z tvojej IP
  - [ ] Port 8501 (Frontend) - verejný prístup
  - [ ] Port 8000 (Backend API) - voliteľné
- [ ] Flexible IP pripojený k instance
- [ ] PostgreSQL database connection string pripravený
- [ ] S3 bucket existuje a je dostupný
- [ ] Mistral API key pripravený

### Credentials Checklist

Uisti sa, že máš všetky tieto údaje pripravené:

```env
MISTRAL_API_KEY=sk-...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET_NAME=ai-claims-docs
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par
DATABASE_URL=postgresql://user:pass@host:port/db
SCW_DEFAULT_ORGANIZATION_ID=...
SCW_DEFAULT_PROJECT_ID=...
```

### Deployment Kroky

#### Krok 1: Pripojenie na Scaleway Instance
```bash
ssh root@<SCALEWAY_IP>
```

#### Krok 2: System Setup
```bash
# Stiahnuť a spustiť setup script
curl -o setup.sh https://raw.githubusercontent.com/yourusername/ai-claims-scaleway-python/main/deploy/setup.sh
chmod +x setup.sh
./setup.sh
```

- [ ] Docker nainštalovaný
- [ ] Docker Compose nainštalovaný
- [ ] Git nainštalovaný
- [ ] Vytvorený `/opt/ai-claims` adresár

#### Krok 3: Clone Repository
```bash
cd /opt/ai-claims
git clone https://github.com/yourusername/ai-claims-scaleway-python.git .
```

- [ ] Repository naklonovaný
- [ ] Všetky súbory prítomné

#### Krok 4: Konfigurácia Environment
```bash
nano .env
```

Skopíruj a vyplň všetky premenné z `.env.example`

- [ ] `.env` súbor vytvorený
- [ ] Všetky premenné vyplnené
- [ ] Database URL správne (špeciálne znaky URL-encoded)
- [ ] S3 credentials overené
- [ ] Mistral API key overený

#### Krok 5: Deploy Aplikácie
```bash
chmod +x deploy/install.sh
./deploy/install.sh
```

- [ ] Docker images stiahnuté/buildnuté
- [ ] Všetky služby spustené
- [ ] Database migrations úspešné

#### Krok 6: Verifikácia Deploymentu

```bash
# Status check
docker compose ps
```

- [ ] Backend: Running
- [ ] Worker: Running
- [ ] Frontend: Running
- [ ] Redis: Running
- [ ] Presidio: Running (healthy)

```bash
# Health checks
curl http://localhost:8000/claims/
curl http://localhost:8001/health
docker compose exec redis redis-cli ping
```

- [ ] Backend API odpovedá
- [ ] Presidio API je healthy
- [ ] Redis odpovedá PONG

#### Krok 7: Testovanie Frontend
```bash
# Otvor v prehliadači
http://<SCALEWAY_IP>:8501
```

- [ ] Frontend sa načíta
- [ ] Môžeš nahrať PDF
- [ ] OCR processing funguje
- [ ] Anonymizácia funguje
- [ ] AI analýza funguje

### Post-deployment

#### Monitoring
```bash
# Real-time logs
docker compose logs -f

# Špecifické služby
docker compose logs -f worker
docker compose logs -f presidio
```

#### Zálohovanie
```bash
# Backup .env
cp /opt/ai-claims/.env /root/.env.backup

# Backup config
cp /opt/ai-claims/config/settings.yaml /root/settings.yaml.backup
```

- [ ] `.env` zazálohovaný
- [ ] `settings.yaml` zazálohovaný

#### Security
```bash
# Firewall (ufw)
apt-get install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow from <TVOJA_IP> to any port 22
ufw allow 8501
ufw allow 8000  # optional
ufw enable
```

- [ ] UFW nakonfigurovaný
- [ ] SSH len z tvojej IP
- [ ] Frontend port otvorený

## 🚨 Troubleshooting Guide

### Problem: Presidio nefunguje

**Symptómy:**
- Worker logy: `Failed to resolve 'presidio'`
- Worker logy: `Connection refused`

**Riešenie:**
```bash
# 1. Check Presidio logs
docker compose logs presidio

# 2. Check health
curl http://localhost:8001/health

# 3. Rebuild if needed
docker compose build --no-cache presidio
docker compose up -d presidio

# 4. Restart worker
docker compose restart worker
```

### Problem: Worker nespracováva úlohy

**Symptómy:**
- Dokumenty ostávajú v stave "Processing"
- Worker logy: Žiadna aktivita

**Riešenie:**
```bash
# 1. Check Redis
docker compose logs redis
docker compose exec redis redis-cli ping

# 2. Check worker logs
docker compose logs worker

# 3. Restart
docker compose restart worker redis
```

### Problem: Database connection error

**Symptómy:**
- Backend logy: `Connection refused`
- Backend logy: `Authentication failed`

**Riešenie:**
```bash
# 1. Test connection manually
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME>

# 2. Check .env
cat .env | grep DATABASE_URL

# 3. URL-encode špeciálne znaky v hesle
# ? → %3F, @ → %40, : → %3A, / → %2F

# 4. Restart backend
docker compose restart backend
```

### Problem: Frontend nedostupný

**Symptómy:**
- Browser: Connection refused
- Frontend logy: Chyby

**Riešenie:**
```bash
# 1. Check frontend logs
docker compose logs frontend

# 2. Check backend connection
curl http://localhost:8000/claims/

# 3. Restart
docker compose restart frontend backend
```

## 📊 Performance Monitoring

### Resource Usage
```bash
# Container stats
docker stats

# Disk space
df -h

# Memory usage
free -h
```

### Logs
```bash
# Tail logs
docker compose logs -f --tail=100

# Search logs
docker compose logs worker | grep ERROR
docker compose logs presidio | grep WARNING
```

## 🔄 Updates

### Update Aplikácie
```bash
cd /opt/ai-claims
./deploy/update.sh
```

### Manual Update
```bash
cd /opt/ai-claims
git pull origin main
docker compose build --no-cache
docker compose up -d
```

## 📞 Support

Ak narazíš na problémy:

1. Skontroluj logy: `docker compose logs -f`
2. Pozri dokumentáciu: `deploy/README.md`
3. Otvor GitHub Issue s logmi a popisom problému

## ✅ Final Checklist

Pred oznámením že deployment je hotový:

- [ ] Všetky služby bežia (docker compose ps)
- [ ] Frontend je dostupný cez verejnú IP
- [ ] Môžeš nahrať a spracovať testovací dokument
- [ ] OCR funguje
- [ ] Anonymizácia funguje
- [ ] AI analýza funguje
- [ ] Môžeš stiahnuť report
- [ ] Logy neobsahujú kritické chyby
- [ ] Credentials sú zazálohované
- [ ] Firewall je nakonfigurovaný

---

**Poznámka**: Tento checklist je pre production testovanie. Pre enterprise deployment pridaj monitoring, alerting, backups a CI/CD.

