# 🪟 Windows Setup Guide

## 🚀 Rýchly Štart (Windows)

### 1️⃣ Prvé Spustenie (Lokálny Vývoj)

```powershell
# Vytvor .env.local
Copy-Item .env.example .env.local

# Uprav .env.local - otvorí sa v Notepade
notepad .env.local
```

**Dôležité nastavenia v `.env.local`:**
```bash
# Pridaj Mistral API key (RECOMMENDED - GDPR compliant):
MISTRAL_API_KEY=tvoj_skutocny_mistral_key_sem

# Alternative (optional):
# GEMINI_API_KEY=tvoj_gemini_key_sem

# Vygeneruj secret (v PowerShell):
# [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
BETTER_AUTH_SECRET=vygenerovany-secret-min-32-znakov
```

```powershell
# Spusti lokálne prostredie
.\start-local.ps1
```

### 2️⃣ Produkcia (Na Serveri)

```powershell
# SSH na server a prejdi do projektu
cd /path/to/project

# Vytvor .env.production
Copy-Item .env.example .env.production

# Uprav .env.production
nano .env.production
# alebo
notepad .env.production
```

**Dôležité nastavenia pre PRODUKCIU:**
```bash
ENVIRONMENT=production

# URLs
FRONTEND_URL=https://ai-claims.novis.eu
NEXT_PUBLIC_API_URL=https://ai-claims.novis.eu
NEXT_PUBLIC_APP_URL=https://ai-claims.novis.eu
BETTER_AUTH_URL=https://ai-claims.novis.eu

# Strong secret (generate: openssl rand -base64 32)
BETTER_AUTH_SECRET=production-strong-secret-min-64-chars

# Real SMTP credentials
SMTP_USER=noreply@novis.eu
SMTP_PASSWORD=real_app_password_here
```

```powershell
# Spusti produkciu
.\start-prod.ps1
```

---

## 📋 PowerShell Skripty

| Skript | Účel |
|--------|------|
| `.\start-local.ps1` | Spusti lokálny development |
| `.\start-prod.ps1` | Spusti produkciu |
| `.\stop.ps1` | Zastav všetky služby |
| `.\logs.ps1` | Zobraz logy |
| `.\logs.ps1 frontend` | Logy len pre frontend |
| `.\status.ps1` | Status kontajnerov |

---

## 🔧 Bežné Príkazy

### Spustenie

```powershell
# Lokálny vývoj
.\start-local.ps1

# Produkcia
.\start-prod.ps1
```

### Monitorovanie

```powershell
# Status
.\status.ps1

# Všetky logy
.\logs.ps1

# Konkrétna služba
.\logs.ps1 frontend
.\logs.ps1 backend
.\logs.ps1 worker
```

### Zastavenie

```powershell
# Zastav všetko
.\stop.ps1

# Reštart
.\stop.ps1
.\start-local.ps1
```

### Rebuild

```powershell
# Rebuild všetkého
docker compose build --no-cache

# Rebuild len frontend
docker compose build --no-cache frontend
docker compose up -d frontend

# Reštart služby
docker compose restart backend
docker compose restart frontend
```

---

## 🐛 Riešenie Problémov

### 1. **"make: command not found"**

✅ **Riešené** - použíš PowerShell skripty namiesto `make`:

```powershell
# Namiesto: make local
.\start-local.ps1

# Namiesto: make prod
.\start-prod.ps1
```

---

### 2. **"Cannot find path .env.example"**

```powershell
# Over či existuje
Test-Path .env.example

# Ak nie, vytvor ho:
notepad .env.example
# Skopíruj obsah z README-SETUP.md
```

---

### 3. **"Execution policy" error**

```powershell
# Povoľ spúšťanie skriptov (len raz)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Potom spusti znova
.\start-local.ps1
```

---

### 4. **Aplikácia je pomalá (produkcia)**

```powershell
# Over že používaš production build
Get-Content .env | Select-String "ENVIRONMENT"
# Malo by byť: ENVIRONMENT=production

# Rebuild frontend s production Dockerfile
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d frontend
```

---

### 5. **Auth nefunguje správne**

```powershell
# Over Better Auth premenné
Get-Content .env | Select-String "BETTER_AUTH"

# Malo by byť:
# BETTER_AUTH_SECRET=...
# BETTER_AUTH_URL=https://ai-claims.novis.eu
# DATABASE_URL=postgresql://...

# Reštartuj frontend
docker compose restart frontend
```

---

### 6. **Dokumenty sa nenačítavajú (I/O error)**

```powershell
# Over MinIO
docker compose exec minio mc ls local/ai-claims

# Over S3 nastavenia
Get-Content .env | Select-String "S3_"

# Reštartuj backend
docker compose restart backend
```

---

### 7. **Email nefunguje**

```powershell
# Skontroluj SMTP
Get-Content .env | Select-String "SMTP"

# Musí byť vyplnené:
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# Vytvor App Password:
# https://myaccount.google.com/apppasswords

# Reštartuj worker
docker compose restart worker
```

---

## 📝 Vytvorenie .env.local (Prvýkrát)

```powershell
# 1. Skopíruj template
Copy-Item .env.example .env.local

# 2. Otvor v editore
notepad .env.local

# 3. Uprav tieto riadky:
```

```bash
# Pridaj Mistral API key (RECOMMENDED - GDPR compliant)
MISTRAL_API_KEY=tvoj_mistral_key_sem

# Vygeneruj secret v PowerShell:
# [Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
BETTER_AUTH_SECRET=wvX8kL...vygenerovany_secret
```

```powershell
# 4. Ulož a zavri Notepad

# 5. Spusti
.\start-local.ps1
```

---

## 🌍 Deployment na Produkčný Server

### Na Serveri (Linux)

Ak je server **Linux**, môžeš použiť `make` príkazy:

```bash
make local   # Lokálne
make prod    # Produkcia
make stop    # Zastav
make logs    # Logy
```

### Na Serveri (Windows Server)

Použiš `.ps1` skripty rovnako ako lokálne:

```powershell
.\start-prod.ps1
.\logs.ps1
.\stop.ps1
```

---

## 🎯 Rozdiely: Local vs Production

| Vlastnosť | Local | Production |
|-----------|-------|------------|
| **Dockerfile** | `Dockerfile.dev` | `Dockerfile.prod` |
| **Hot Reload** | ✅ Áno | ❌ Nie |
| **Optimalizácia** | Minimálna | Maximálna |
| **URLs** | localhost:3000 | https://ai-claims.novis.eu |
| **SMTP** | Voliteľné | Povinné (pre emails) |
| **Resources** | Unlimited | Limited (CPU/RAM) |
| **Volumes** | Mounted (live edit) | Copied (immutable) |

---

## ✅ Checklist Pre Produkčný Deployment

- [ ] `.env.production` vytvorený
- [ ] `ENVIRONMENT=production` nastavené
- [ ] Production URLs (`https://ai-claims.novis.eu`)
- [ ] Strong `BETTER_AUTH_SECRET` (min 32 chars)
- [ ] Real SMTP credentials
- [ ] Database URL správne
- [ ] Testované lokálne pred deploymentom
- [ ] Backup databázy pred updateom

---

**Všetko pripravené! Teraz spusti `.\start-local.ps1` a testuj!** 🚀

