# AI Claims Scaleway Deployment Guide

Kompletný návod na nasadenie AI Claims Processing systému na Scaleway s verejným prístupom z internetu.

## Architektúra

```
Internet
    ↓
Scaleway Instance (Public IP)
    ↓
Docker Compose Stack:
- Frontend (Streamlit) :8501
- Backend (FastAPI) :8000
- Worker (Celery)
- Redis :6379
- Presidio API :8001
    ↓
Scaleway Managed PostgreSQL (existujúce)
Scaleway Object Storage S3 (existujúce)
```

## Požiadavky

### Scaleway Resources
- **Instance**: DEV1-M alebo väčší (3GB RAM, 2 vCPU)
- **Managed PostgreSQL**: Už existuje
- **Object Storage S3**: Už existuje (bucket: ai-claims-docs)

### Credentials
Pred nasadením potrebuješ:
- Mistral API Key
- Scaleway S3 Access Key a Secret Key
- Scaleway PostgreSQL connection string
- Scaleway Organization ID a Project ID

## Krok 1: Vytvorenie Scaleway Instance

1. Prihlás sa do [Scaleway Console](https://console.scaleway.com)
2. Naviguj na **Compute → Instances**
3. Klikni **Create Instance**

### Instance Configuration:
```
- Name: ai-claims-production
- Availability Zone: fr-par-1 (alebo fr-par-2)
- Instance Type: DEV1-M (3GB RAM, 2 vCPU, 40GB SSD)
- Image: Ubuntu 22.04 LTS
- IP: Attach a new flexible IP (odporúčané)
```

### Security Group Configuration:
```
Inbound Rules:
  - SSH (TCP 22) - Len tvoja IP adresa
  - HTTP (TCP 8501) - 0.0.0.0/0 (Streamlit Frontend)
  - API (TCP 8000) - 0.0.0.0/0 (Optional - FastAPI Backend)

Outbound Rules:
  - Allow all (default)
```

4. Klikni **Create Instance**
5. Počkaj kým sa instance vytvorí a poznač si **Public IP**

## Krok 2: Initial Server Setup

SSH do tvojho nového servera:

```bash
ssh root@<scaleway-instance-ip>
```

### Automatický Setup

```bash
# Download a spusti setup script
curl -o setup.sh https://raw.githubusercontent.com/Abra7abra7/ai-claims-scaleway-python/main/deploy/setup.sh
chmod +x setup.sh
./setup.sh
```

Tento script:
- Aktualizuje systém
- Nainštaluje Docker & Docker Compose
- Nainštaluje Git a ďalšie nástroje
- Vytvorí `/opt/ai-claims` adresár

### Manuálny Setup (ak preferuješ)

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
apt-get install -y docker-compose-plugin

# Install Git
apt-get install -y git curl

# Create app directory
mkdir -p /opt/ai-claims
```

## Krok 3: Clone Repository a Konfigurácia

```bash
cd /opt/ai-claims

# Clone repository
git clone https://github.com/Abra7abra7/ai-claims-scaleway-python.git .

# Copy environment template
cp .env.example .env
```

## Krok 4: Konfigurácia Environment Variables

Edituj `.env` súbor:

```bash
nano .env
```

Vyplň všetky potrebné hodnoty:

```env
# Mistral AI API
MISTRAL_API_KEY=your_mistral_api_key_here

# Scaleway Object Storage (S3)
S3_ACCESS_KEY=your_s3_access_key
S3_SECRET_KEY=your_s3_secret_key
S3_BUCKET_NAME=ai-claims-docs
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par

# Scaleway Managed PostgreSQL
DATABASE_URL=postgresql://username:password@host:port/database

# Scaleway Project Info
SCW_DEFAULT_ORGANIZATION_ID=your_org_id
SCW_DEFAULT_PROJECT_ID=your_project_id

# Redis (internal Docker network)
REDIS_URL=redis://redis:6379/0
```

**Poznámka**: Ak heslo obsahuje špeciálne znaky, URL-encode ich:
- `?` → `%3F`
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`

Uložy a zavry (Ctrl+X, Y, Enter)

## Krok 5: Deploy Aplikácie

```bash
chmod +x deploy/install.sh
./deploy/install.sh
```

Tento script:
- Stiahne Docker images
- Spustí všetky služby (backend, worker, frontend, redis, presidio)
- Počká 10 sekúnd na inicializáciu
- Spustí database migrations
- Vypíše prístupové URLs

### Výstup by mal vyzerať takto:

```
✅ Application deployed
Frontend: http://51.159.XXX.XXX:8501
Backend: http://51.159.XXX.XXX:8000
```

## Krok 6: Verifikácia Deploymentu

### Skontroluj status služieb

```bash
cd /opt/ai-claims
docker compose ps
```

Všetky služby by mali byť `running`.

### Skontroluj logs

```bash
# Všetky služby
docker compose logs -f

# Špecifická služba
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f frontend
```

### Otestuj prístup

1. **Frontend**: Otvor v prehliadači `http://<scaleway-ip>:8501`
2. **Backend API**: `curl http://<scaleway-ip>:8000/claims/`
3. **Presidio Health**: `curl http://localhost:8001/health`

## Krok 7: Prvé Použitie

1. Otvor frontend URL vo webovom prehliadači
2. Nahraj testovacie PDF dokumenty
3. Skontroluj OCR Review stránku
4. Schváľ OCR výstupy
5. Skontroluj Anonymization Review stránku
6. Schváľ anonymizované dokumenty
7. Spusti AI analýzu cez Admin Dashboard

## Údržba a Monitoring

### Reštart služieb

```bash
cd /opt/ai-claims
docker compose restart
```

### Reštart konkrétnej služby

```bash
docker compose restart backend
docker compose restart worker
docker compose restart frontend
```

### Update aplikácie

```bash
cd /opt/ai-claims
./deploy/update.sh
```

### Monitoring logs v real-time

```bash
# Všetky služby
docker compose logs -f

# Backend only
docker compose logs -f backend

# Worker only (tu sa vykonávajú OCR, cleaning, anonymization tasks)
docker compose logs -f worker
```

### Kontrola využitia resources

```bash
docker stats
```

### Database pripojenie (troubleshooting)

```bash
# Pripoj sa k PostgreSQL
psql -h 51.159.74.55 --port 23504 -d rdb -U username

# V psql konzole:
\dt  # List tables
SELECT * FROM claims LIMIT 5;  # Query claims
\q   # Exit
```

## Troubleshooting

### Backend sa nespustí

```bash
# Check logs
docker compose logs backend

# Skontroluj DATABASE_URL v .env
cat .env | grep DATABASE_URL

# Reštart
docker compose restart backend
```

### Worker nespracováva úlohy

```bash
# Check worker logs
docker compose logs worker

# Check Redis
docker compose logs redis

# Reštart worker a redis
docker compose restart worker redis
```

### Frontend nedostupný

```bash
# Check frontend logs
docker compose logs frontend

# Check backend connection
curl http://localhost:8000/claims/

# Reštart
docker compose restart frontend
```

### Presidio API nefunguje

```bash
# Check presidio logs
docker compose logs presidio

# Check health
curl http://localhost:8001/health

# Reštart
docker compose restart presidio
```

### Database connection error

```bash
# Overť že PostgreSQL je accessible
nc -zv 51.159.74.55 23504

# Overť credentials
psql -h 51.159.74.55 --port 23504 -d rdb -U username

# Overť URL encoding special characters v hesle
```

## Security Best Practices

### 1. SSH Security

```bash
# Disable password authentication
nano /etc/ssh/sshd_config

# Set these values:
PasswordAuthentication no
PermitRootLogin prohibit-password

# Restart SSH
systemctl restart sshd
```

### 2. Firewall (ufw)

```bash
# Install ufw
apt-get install -y ufw

# Configure rules
ufw default deny incoming
ufw default allow outgoing
ufw allow from YOUR_IP to any port 22  # SSH len z tvojej IP
ufw allow 8501  # Streamlit Frontend
ufw allow 8000  # FastAPI Backend (optional)

# Enable
ufw enable
ufw status
```

### 3. Regular Updates

```bash
# Setup unattended upgrades
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### 4. Backup Strategy

```bash
# Backup PostgreSQL (na Scaleway Console alebo CLI)
# Backup .env súboru
cp /opt/ai-claims/.env /root/.env.backup

# Backup config
cp /opt/ai-claims/config/settings.yaml /root/settings.yaml.backup
```

## Optional: Domain & HTTPS Setup

Ak máš vlastnú doménu:

### 1. Nastav DNS A záznam

```
Type: A
Name: claims (alebo @)
Value: <scaleway-instance-ip>
```

### 2. Install Nginx Reverse Proxy

```bash
apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx config
cat > /etc/nginx/sites-available/ai-claims << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable config
ln -s /etc/nginx/sites-available/ai-claims /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 3. Install SSL Certificate

```bash
# Let's Encrypt SSL
certbot --nginx -d your-domain.com

# Auto-renewal is setup automatically
certbot renew --dry-run
```

### 4. Update Security Group

```
# V Scaleway Console, pridaj rule:
- HTTPS (TCP 443) - 0.0.0.0/0
```

Teraz budeš môcť pristupovať na `https://your-domain.com`

## Cost Estimation

**Mesačné náklady:**
- Instance DEV1-M: ~€11/mesiac
- PostgreSQL: Už máš
- Object Storage: Už máš
- Public IP: Free (ak je attached)

**Celkom nové náklady: ~€11/mesiac**

## Monitoring a Alerts

### Monitoring s Scaleway Console

1. Navštív Scaleway Console → Instance → ai-claims-production
2. Tab "Metrics" zobrazuje:
   - CPU utilization
   - Network traffic
   - Disk I/O

### Log Rotation

```bash
# Docker už má built-in log rotation
# Ale môžeš to nastaviť v docker-compose.yml:

# V každom service pridaj:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Getting Help

- **GitHub Issues**: https://github.com/Abra7abra7/ai-claims-scaleway-python/issues
- **Scaleway Support**: https://console.scaleway.com/support
- **Documentation**: `/opt/ai-claims/README.md`

## Quick Reference

```bash
# Status check
cd /opt/ai-claims && docker compose ps

# View logs
docker compose logs -f

# Restart all
docker compose restart

# Update app
./deploy/update.sh

# Stop all
docker compose down

# Start all
docker compose up -d

# Full rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

**Poznámka**: Tento deployment guide je pre production testovanie. Pre plný production deployment odporúčame pridať:
- Load balancer
- Auto-scaling
- Monitoring & alerting (Prometheus + Grafana)
- Centralized logging (ELK stack)
- Backup automation
- CI/CD pipeline


