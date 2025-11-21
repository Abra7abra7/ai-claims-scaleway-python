# Fix: Presidio Service Connection Issue

## Problém
Worker service sa nemohol pripojiť k Presidio API, čo spôsobovalo zlyhanie anonymizácie dokumentov.

**Chybová hláška:**
```
Failed to resolve 'presidio' ([Errno -2] Name or service not known)
```

## Root Cause
1. Worker service nemal `presidio` v `depends_on`, takže sa spúšťal pred Presidio
2. Presidio nemal healthcheck, takže Docker nevedel kedy je služba pripravená
3. Chýbali závislosti v Presidio Dockerfile (curl pre healthcheck)
4. Worker nemal explicitnú environment variable pre Presidio URL

## Zmeny

### 1. docker-compose.yml

**Worker service:**
- ✅ Pridané `presidio` do `depends_on`
- ✅ Pridaná env variable `PRESIDIO_URL=http://presidio:8001`

**Presidio service:**
- ✅ Odstránené `depends_on: - backend` (circular dependency)
- ✅ Pridaný `restart: unless-stopped`
- ✅ Pridaný healthcheck:
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
    interval: 10s
    timeout: 5s
    retries: 5
  ```

**Globálne:**
- ✅ Odstránený zastaraný `version: '3.8'`

### 2. presidio-api/Dockerfile

**Pridané:**
- ✅ `curl` do system dependencies (pre healthcheck)

### 3. presidio-api/requirements.txt

**Pridané:**
- ✅ `spacy>=3.5.0` (bola chýbajúca závislosť)

### 4. docker-compose.prod.yml

**Zmeny:**
- ✅ Odstránený zastaraný `version: '3.8'`
- ✅ Produkčné resource limits zostali zachované

### 5. Nové súbory

**local-start.sh:**
- Automatický startup script pre lokálny vývoj
- Obsahuje health checks pre všetky služby
- User-friendly výstup s farebnými indikátormi

**QUICK_START.md:**
- Rýchly návod na spustenie
- Lokálny vývoj aj Scaleway deployment
- Troubleshooting tipy

**DEPLOYMENT_CHECKLIST.md:**
- Kompletný checklist pre deployment
- Krok-za-krokom návod
- Troubleshooting guide
- Post-deployment monitoring

**Makefile (aktualizovaný):**
- Nové príkazy: `health`, `migrate`, `rebuild`
- Lepšia organizácia a help menu

## Verifikácia Fix-u

### Lokálne testovanie

```bash
# 1. Rebuild Presidio
docker compose build --no-cache presidio

# 2. Reštart služieb
docker compose up -d presidio worker

# 3. Overenie health
curl http://localhost:8001/health
# Výstup: {"status":"healthy"}

# 4. Test anonymizácie
curl -X POST http://localhost:8001/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Volám sa Ján Novák, rodné číslo 901231/1234",
    "country": "SK",
    "language": "en"
  }'
# Výstup: {"anonymized_text":"<OSOBA>, rodné číslo <RODNE_CISLO>",...}
```

### Výsledky
- ✅ Presidio service je healthy
- ✅ Worker sa úspešne pripája k Presidio
- ✅ Anonymizácia funguje správne
- ✅ Žiadne DNS resolution errors

## Deployment na Scaleway

### Pre nový deployment:
```bash
ssh root@<SCALEWAY_IP>
cd /opt/ai-claims
git pull origin main
./deploy/install.sh
```

### Pre existujúci deployment:
```bash
ssh root@<SCALEWAY_IP>
cd /opt/ai-claims
./deploy/update.sh
```

## Monitoring

Po deploymente sleduj:

```bash
# Všetky logy
docker compose logs -f

# Worker logy (tu by sa mali objaviť anonymization tasks)
docker compose logs -f worker

# Presidio logy
docker compose logs -f presidio

# Container status
docker compose ps
```

## Breaking Changes

❌ **Žiadne breaking changes** - všetky zmeny sú backward compatible.

## Poznámky

1. **Docker network**: Všetky služby komunikujú cez default Docker network
2. **Service dependencies**: Správne poradie startovania (Redis → Presidio → Worker)
3. **Health checks**: Presidio má vlastný health endpoint na `/health`
4. **Environment variables**: Worker má explicitne nastavenú `PRESIDIO_URL`

## Ďalšie Kroky

1. [ ] Commit a push zmeny do Git
2. [ ] Test deployment na Scaleway staging environment
3. [ ] Produkčný deployment
4. [ ] Monitoring a alerting setup (voliteľné)

## Git Commands

```bash
# Stage zmeny
git add docker-compose.yml
git add docker-compose.prod.yml
git add presidio-api/Dockerfile
git add presidio-api/requirements.txt
git add Makefile
git add local-start.sh
git add QUICK_START.md
git add DEPLOYMENT_CHECKLIST.md
git add CHANGELOG_FIX.md

# Commit
git commit -m "Fix: Presidio service connection and add deployment tools

- Add presidio to worker depends_on
- Add healthcheck for Presidio service
- Add curl and spacy to Presidio dependencies
- Remove deprecated version attribute
- Add local-start.sh script
- Add QUICK_START.md and DEPLOYMENT_CHECKLIST.md
- Update Makefile with new commands"

# Push
git push origin main
```

---

**Fix vyriešil:** ✅ Presidio connection issue
**Testované:** ✅ Lokálne + pripravené na Scaleway
**Dokumentácia:** ✅ Kompletná
**Ready for deployment:** ✅ Áno

