# 🚀 Multi-Environment Setup Guide

## 📋 Rýchly Štart

### Lokálny Vývoj

```bash
# 1. Vytvor .env.local (len prvýkrát)
cp .env.example .env.local
nano .env.local  # vyplň svoje API keys

# 2. Spusti lokálne prostredie
make local

# 3. Otvor v prehliadači
# Frontend:  http://localhost:3000
# API Docs:  http://localhost:8000/api/v1/docs
# MinIO:     http://localhost:9001
```

### Produkcia (na serveri)

```bash
# 1. Vytvor .env.production (len prvýkrát)
cp .env.example .env.production
nano .env.production  # vyplň produkčné credentials

# 2. Spusti produkčné prostredie
make prod

# 3. Over že beží
make status
make logs
```

---

## 📁 Súbory Pre Rôzne Prostredia

| Súbor | Účel | Commituj? |
|-------|------|-----------|
| `.env.example` | Template | ✅ Áno |
| `.env.local` | Lokálny vývoj | ❌ NIE |
| `.env.production` | Produkcia | ❌ NIE |
| `docker-compose.yml` | Base config | ✅ Áno |
| `docker-compose.local.yml` | Local overrides | ✅ Áno |
| `docker-compose.prod.yml` | Production overrides | ✅ Áno |
| `Dockerfile.dev` | Dev build | ✅ Áno |
| `Dockerfile.prod` | Prod build | ✅ Áno |
| `Makefile` | Pomocné príkazy | ✅ Áno |

---

## 🎯 Make Príkazy

### Základné

```bash
make help          # Zobraz všetky príkazy
make local         # Spusti lokálne prostredie
make prod          # Spusti produkčné prostredie
make stop          # Zastav všetky služby
make restart       # Reštartuj (detekuje prostredie)
```

### Logy

```bash
make logs              # Všetky logy
make logs-frontend     # Len frontend
make logs-backend      # Len backend
make logs-worker       # Len worker
```

### Build & Clean

```bash
make build             # Rebuild všetkých images
make rebuild-frontend  # Rebuild len frontend
make rebuild-backend   # Rebuild len backend
make clean             # Vymaž všetko (vrátane volumes)
```

### Utility

```bash
make status            # Status kontajnerov
make shell-backend     # Bash do backend kontajnera
make shell-frontend    # Shell do frontend kontajnera
make shell-db          # PostgreSQL shell
make db-backup         # Backup databázy
```

---

## 🔑 Premenné Prostredia

### Vyžadované

```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...      # Generate: openssl rand -base64 32
MISTRAL_API_KEY=...         # RECOMMENDED - GDPR compliant (Gemini ako fallback)
```

### Storage (MinIO / Scaleway)

```bash
# Lokálne (MinIO)
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123

# Produkcia (Scaleway)
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_ACCESS_KEY=<scaleway_key>
S3_SECRET_KEY=<scaleway_secret>
```

### Email (voliteľné)

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # https://myaccount.google.com/apppasswords
```

---

## 🔄 Workflow

### Lokálny Vývoj → Produkcia

```bash
# === NA TVOJOM PC ===
make local              # Vývoj lokálne
# ... kóduješ ...
git add .
git commit -m "feat: nova funkcionalita"
git push origin main

# === NA SERVERI ===
ssh user@server
cd /path/to/project
git pull origin main
make prod              # Nasaď produkciu
make logs              # Sleduj logy
```

---

## ⚠️ Dôležité Upozornenia

### 1. **NIKDY necommituj .env súbory s credentials!**

```bash
# ❌ ZLÝCH
git add .env.local
git add .env.production

# ✅ DOBRÉ
git add .env.example
```

### 2. **Vždy používaj make príkazy**

```bash
# ❌ ZLÝCH (môžeš zabudnúť flags)
docker compose up

# ✅ DOBRÉ (automaticky vyberie správny config)
make local
make prod
```

### 3. **Generuj silné secrets**

```bash
# Generate BETTER_AUTH_SECRET
openssl rand -base64 32

# Generate strong password
openssl rand -base64 24
```

---

## 🐛 Troubleshooting

### Aplikácia je pomalá

```bash
# Over že používaš správne prostredie
cat .env | grep ENVIRONMENT

# V produkcii MUSÍ byť:
ENVIRONMENT=production

# Rebuild frontend s production Dockerfile
make rebuild-frontend
```

### Auth nefunguje

```bash
# Over že máš všetky premenné
cat .env | grep -E "(DATABASE_URL|BETTER_AUTH)"

# Reštartuj frontend
make restart-frontend
```

### Dokumenty sa nenačítajú

```bash
# Over MinIO
docker compose exec minio mc ls local/ai-claims

# Over S3 premenné
cat .env | grep S3_

# Reštartuj backend
make restart-backend
```

### Email nefunguje

```bash
# Skontroluj SMTP credentials
cat .env | grep SMTP

# Sleduj worker logy
make logs-worker
```

---

## 📚 Ďalšie Zdroje

- [README.md](README.md) - Hlavná dokumentácia
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Development guide
- [.env.example](.env.example) - Environment template

---

**Všetko funguje? Enjoy coding! 🎉**

