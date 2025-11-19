# Deployment Guide - Scaleway

Tento návod popisuje ako nasadiť AI Claims Processing System na Scaleway.

## Predpoklady

- Scaleway účet
- Scaleway CLI nainštalované a nakonfigurované
- SSH kľúč pre prístup k VM
- Git nainštalovaný lokálne

## Krok 1: Vytvorenie Scaleway Object Storage Bucket

### 1.1 Cez Scaleway Console

1. Prihláste sa do [Scaleway Console](https://console.scaleway.com)
2. Prejdite na **Object Storage** → **Buckets**
3. Kliknite **Create Bucket**
4. Nastavenia:
   - **Name:** `ai-claims-docs` (alebo vlastný názov)
   - **Region:** `fr-par` (Paris)
   - **Visibility:** Private
5. Kliknite **Create Bucket**

### 1.2 Vytvorenie API Keys

1. V Scaleway Console prejdite na **Identity and Access Management** → **API Keys**
2. Kliknite **Generate API Key**
3. Uložte si:
   - **Access Key ID**
   - **Secret Key**

### 1.3 Alternatívne: Cez CLI

```bash
# Vytvorenie bucketu
scw object bucket create name=ai-claims-docs region=fr-par

# Vytvorenie API key (manuálne cez console)
```

## Krok 2: Získanie Mistral AI API Key

1. Registrujte sa na [Mistral AI](https://console.mistral.ai)
2. Prejdite na **API Keys**
3. Vytvorte nový API key
4. Uložte si kľúč

## Krok 3: Vytvorenie Scaleway Virtual Machine

### 3.1 Cez Scaleway Console

1. Prejdite na **Compute** → **Instances**
2. Kliknite **Create Instance**
3. Nastavenia:
   - **Availability Zone:** `fr-par-1`
   - **Instance Type:** `DEV1-M` alebo `GP1-S` (min. 4GB RAM)
   - **Image:** `Ubuntu 22.04 LTS`
   - **Storage:** 20GB Block Storage
   - **IP:** Attach new flexible IP
   - **SSH Key:** Vyberte váš SSH kľúč
4. Kliknite **Create Instance**

### 3.2 Alternatívne: Cez CLI

```bash
scw instance server create \
  type=DEV1-M \
  zone=fr-par-1 \
  image=ubuntu_jammy \
  name=ai-claims-server \
  ip=new
```

### 3.3 Poznámka k IP adrese

- Uložte si **Public IP** vášho VM
- Budete ju potrebovať pre SSH prístup

## Krok 4: Pripojenie na VM a inštalácia závislostí

### 4.1 SSH pripojenie

```bash
ssh root@YOUR_VM_IP
```

### 4.2 Aktualizácia systému

```bash
apt update && apt upgrade -y
```

### 4.3 Inštalácia Docker

```bash
# Inštalácia Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Spustenie Docker
systemctl start docker
systemctl enable docker

# Overenie
docker --version
```

### 4.4 Inštalácia Docker Compose

```bash
# Inštalácia Docker Compose
apt install docker-compose-plugin -y

# Overenie
docker compose version
```

### 4.5 Inštalácia Git

```bash
apt install git -y
```

## Krok 5: Klonovanie projektu

```bash
# Vytvorenie pracovného adresára
mkdir -p /opt/apps
cd /opt/apps

# Klonovanie repozitára
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git
cd ai-claims-scaleway-python
```

## Krok 6: Konfigurácia environment variables

### 6.1 Vytvorenie .env súboru

```bash
cp .env.example .env
nano .env
```

### 6.2 Vyplnenie .env súboru

```bash
# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here

# Scaleway Object Storage (S3)
S3_ACCESS_KEY=your_scaleway_access_key
S3_SECRET_KEY=your_scaleway_secret_key
S3_BUCKET_NAME=ai-claims-docs
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

# Database (pre Docker Compose použite default)
DATABASE_URL=postgresql://postgres:postgres@db:5432/claims_db

# Redis (pre Docker Compose použite default)
REDIS_URL=redis://redis:6379/0
```

**Dôležité:**
- Nahraďte `your_mistral_api_key_here` vašim Mistral API kľúčom
- Nahraďte `your_scaleway_access_key` a `your_scaleway_secret_key` vašimi Scaleway credentials
- Ak ste použili iný názov bucketu, zmeňte `S3_BUCKET_NAME`

### 6.3 Uloženie súboru

V nano editore:
- Stlačte `Ctrl + X`
- Stlačte `Y` pre potvrdenie
- Stlačte `Enter`

## Krok 7: Spustenie aplikácie

### 7.1 Build Docker images

```bash
docker compose build
```

**Poznámka:** Tento krok môže trvať 5-10 minút pri prvom spustení.

### 7.2 Spustenie služieb

```bash
docker compose up -d
```

### 7.3 Overenie že služby bežia

```bash
docker compose ps
```

Očakávaný výstup:
```
NAME                                   STATUS
ai-claims-scaleway-python-backend-1    Up
ai-claims-scaleway-python-db-1         Up
ai-claims-scaleway-python-frontend-1   Up
ai-claims-scaleway-python-redis-1      Up
ai-claims-scaleway-python-worker-1     Up
```

### 7.4 Sledovanie logov

```bash
# Všetky služby
docker compose logs -f

# Konkrétna služba
docker compose logs -f backend
docker compose logs -f worker
```

## Krok 8: Konfigurácia firewall

### 8.1 Cez Scaleway Console

1. Prejdite na **Security Groups**
2. Vyberte security group vášho VM
3. Pridajte pravidlá:
   - **Port 8501** (Streamlit Frontend) - TCP, Inbound, 0.0.0.0/0
   - **Port 8000** (FastAPI Backend) - TCP, Inbound, 0.0.0.0/0 (voliteľné, pre API prístup)
   - **Port 22** (SSH) - TCP, Inbound, Your IP (odporúčané obmedziť)

### 8.2 Alternatívne: UFW na VM

```bash
# Povoliť SSH
ufw allow 22/tcp

# Povoliť Streamlit
ufw allow 8501/tcp

# Povoliť FastAPI (voliteľné)
ufw allow 8000/tcp

# Aktivovať firewall
ufw enable
```

## Krok 9: Prístup k aplikácii

### 9.1 Frontend (Streamlit)

Otvorte v prehliadači:
```
http://YOUR_VM_IP:8501
```

### 9.2 Backend API (FastAPI)

Dokumentácia API:
```
http://YOUR_VM_IP:8000/docs
```

## Krok 10: Testovanie

### 10.1 Test pripojení

```bash
docker compose exec backend python scripts/verify_connections.py
```

Očakávaný výstup:
```
=== Verifying External Connections ===
Testing Mistral AI Connection... SUCCESS
Testing Scaleway S3 Connection... SUCCESS (Bucket 'ai-claims-docs' found)

All external connections look good! You can start the app.
```

### 10.2 Test nahrávania súboru

1. Otvorte frontend: `http://YOUR_VM_IP:8501`
2. Prejdite na "Nahlásenie poistnej udalosti"
3. Nahrajte testovací PDF súbor
4. Prejdite na "Admin Dashboard"
5. Skontrolujte či sa claim zobrazuje

## Údržba a Monitoring

### Reštart služieb

```bash
docker compose restart
```

### Zastavenie služieb

```bash
docker compose down
```

### Aktualizácia aplikácie

```bash
cd /opt/apps/ai-claims-scaleway-python
git pull
docker compose down
docker compose build
docker compose up -d
```

### Zálohovanie databázy

```bash
# Export databázy
docker compose exec db pg_dump -U postgres claims_db > backup_$(date +%Y%m%d).sql

# Import databázy
docker compose exec -T db psql -U postgres claims_db < backup_20241119.sql
```

### Sledovanie využitia zdrojov

```bash
# CPU a RAM
docker stats

# Disk space
df -h

# Docker volumes
docker volume ls
```

### Čistenie starých Docker images

```bash
docker system prune -a
```

## Troubleshooting

### Backend sa nespustí

```bash
# Skontrolujte logy
docker compose logs backend

# Najčastejšie problémy:
# 1. Chýbajúce environment variables v .env
# 2. Nesprávne S3 credentials
# 3. Databáza nie je pripravená (počkajte 10s a reštartujte)
```

### Worker nepracuje

```bash
# Skontrolujte logy
docker compose logs worker

# Reštart worker
docker compose restart worker
```

### Databáza chyby

```bash
# Reštart databázy
docker compose restart db

# Vymazanie databázy a reštart (POZOR: stratíte dáta)
docker compose down -v
docker compose up -d
```

### S3 connection failed

```bash
# Overte credentials
docker compose exec backend python -c "
from app.core.config import get_settings
s = get_settings()
print(f'Access Key: {s.S3_ACCESS_KEY[:10]}...')
print(f'Bucket: {s.S3_BUCKET_NAME}')
print(f'Endpoint: {s.S3_ENDPOINT_URL}')
"

# Overte že bucket existuje v Scaleway Console
```

## Produkčné odporúčania

### 1. HTTPS (SSL/TLS)

Použite reverse proxy (Nginx) s Let's Encrypt:

```bash
apt install nginx certbot python3-certbot-nginx -y

# Konfigurácia Nginx pre Streamlit
nano /etc/nginx/sites-available/ai-claims

# Získanie SSL certifikátu
certbot --nginx -d your-domain.com
```

### 2. Domain meno

- Zaregistrujte doménu
- Nastavte A záznam na IP vášho VM
- Použite Scaleway DNS alebo Cloudflare

### 3. Monitoring

- Nastavte Scaleway Monitoring & Alerting
- Použite Prometheus + Grafana pre detailné metriky
- Nastavte email notifikácie pre downtime

### 4. Zálohovanie

- Automatické zálohy databázy (cron job)
- Scaleway Snapshots pre VM
- S3 bucket versioning

### 5. Škálovanie

- Použite Scaleway Managed Database namiesto Docker PostgreSQL
- Použite Scaleway Managed Redis
- Horizontálne škálovanie workers (viacero VM)

### 6. Bezpečnosť

- Obmedzte SSH prístup len na vašu IP
- Používajte silné heslá
- Pravidelne aktualizujte systém
- Nastavte fail2ban pre SSH
- Používajte secrets management (Scaleway Secret Manager)

## Náklady (približný odhad)

**Mesačné náklady pre PoC:**
- VM (DEV1-M): ~€7-10/mesiac
- Object Storage (10GB): ~€0.20/mesiac
- Flexible IP: €1/mesiac
- Mistral API: Pay-as-you-go (závisí od použitia)

**Celkom: ~€8-12/mesiac** (bez Mistral API usage)

## Podpora

Pre problémy s:
- **Scaleway:** https://console.scaleway.com/support
- **Mistral AI:** https://docs.mistral.ai
- **Aplikáciou:** GitHub Issues na https://github.com/Abra7abra7/ai-claims-scaleway-python
