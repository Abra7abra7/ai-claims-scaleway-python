# Architektúra AI Claims Processing System

## Prehľad

Tento systém automatizuje spracovanie poistných nárokov pomocou AI. Umožňuje nahrávanie dokumentov, automatickú extrakciu textu (OCR), anonymizáciu citlivých údajov a AI analýzu nárokov.

## Komponenty systému

### 1. Frontend (Streamlit)
**Súbor:** `frontend/app.py`

**Funkcie:**
- **Nahlásenie poistnej udalosti** - Stránka pre nahrávanie PDF dokumentov
- **Admin Dashboard** - Prehľad všetkých nárokov s možnosťou schválenia a analýzy

**Workflow:**
1. Používateľ nahrá jeden alebo viac PDF súborov
2. Súbory sa odošlú na backend API endpoint `/upload/`
3. Dashboard zobrazuje zoznam všetkých claims a ich dokumentov
4. Admin môže vybrať typ AI analýzy a schváliť claim

### 2. Backend API (FastAPI)
**Súbor:** `app/main.py`

**Endpointy:**

#### `POST /upload/`
- Prijíma viacero PDF súborov
- Vytvorí jeden `Claim` záznam
- Pre každý súbor:
  - Nahrá do Scaleway S3 (`claims/{claim_id}/{filename}`)
  - Vytvorí `ClaimDocument` záznam v databáze
  - Spustí Celery task `process_claim` pre spracovanie

#### `GET /claims/`
- Vráti zoznam všetkých claims
- Každý claim obsahuje pole `documents` s detailmi dokumentov

#### `GET /claims/{claim_id}`
- Vráti detail konkrétneho claim

#### `GET /prompts/`
- Vráti zoznam dostupných AI prompt šablón

#### `POST /approve/{claim_id}`
- Prijíma `prompt_id` v request body
- Spustí Celery task `analyze_claim_task` s vybraným promptom

### 3. Worker (Celery)
**Súbor:** `app/worker.py`

**Tasks:**

#### `process_claim(document_id)`
**Účel:** Spracovanie jednotlivého dokumentu

**Kroky:**
1. **Získanie presigned URL** - Vytvorí dočasný odkaz na súbor v S3
2. **OCR** - Zavolá Mistral Document AI API s presigned URL
3. **Anonymizácia** - Použije Microsoft Presidio na anonymizáciu textu
4. **Uloženie** - Uloží `original_text` a `anonymized_text` do databázy
5. **Kontrola** - Skontroluje či sú všetky dokumenty v claim spracované
6. **Aktualizácia statusu** - Ak áno, zmení status na `WAITING_FOR_APPROVAL`

**Anonymizované entity:**
- `PERSON` → `<OSOBA>`
- `PHONE_NUMBER` → `<TELEFON>`
- `EMAIL_ADDRESS` → `<EMAIL>`
- `SK_RODNE_CISLO` → `<RODNE_CISLO>` (Slovak birth number)
- `SK_IBAN` → `<IBAN>`

#### `analyze_claim_task(claim_id, custom_prompt)`
**Účel:** AI analýza claim

**Kroky:**
1. **Agregácia textu** - Spojí anonymizovaný text zo všetkých dokumentov
2. **AI Analýza** - Zavolá Mistral Chat API s vybraným promptom
3. **Uloženie výsledku** - Uloží JSON výsledok do `analysis_result`
4. **Aktualizácia statusu** - Zmení status na `ANALYZED`

**Výstup analýzy (JSON):**
```json
{
  "recommendation": "APPROVE|REJECT|INVESTIGATE",
  "confidence": 0.0-1.0,
  "reasoning": "Detailné vysvetlenie",
  "missing_info": ["zoznam chýbajúcich informácií"]
}
```

### 4. Databáza (PostgreSQL + pgvector)
**Súbory:** `app/db/models.py`, `app/db/session.py`

**Tabuľky:**

#### `claims`
```sql
- id: SERIAL PRIMARY KEY
- created_at: TIMESTAMP
- status: VARCHAR (PROCESSING, WAITING_FOR_APPROVAL, ANALYZED)
- analysis_result: JSONB
```

#### `claim_documents`
```sql
- id: SERIAL PRIMARY KEY
- claim_id: INTEGER (FK -> claims.id)
- filename: VARCHAR
- s3_key: VARCHAR
- original_text: TEXT
- anonymized_text: TEXT
- embedding: VECTOR(1024)
```

**Vzťahy:**
- `Claim` má viacero `ClaimDocument` (1:N)

### 5. Services

#### Storage Service (`app/services/storage.py`)
**Funkcie:**
- `upload_bytes(file_content, s3_key, content_type)` - Nahrá súbor do S3
- `generate_presigned_url(s3_key)` - Vytvorí dočasný odkaz (platnosť 1 hodina)
- `download_file(s3_key, local_path)` - Stiahne súbor z S3

#### OCR Service (`app/services/ocr.py`)
**Funkcie:**
- `extract_text_from_url(presigned_url)` - Zavolá Mistral Document AI OCR API

**API Call:**
```python
client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "document_url", "document_url": presigned_url}
)
```

#### Anonymizer Service (`app/services/anonymizer.py`)
**Funkcie:**
- `anonymize(text)` - Anonymizuje text pomocou Presidio

**Custom recognizers:**
- Slovak Rodné číslo: `\b\d{6}[/]?\d{3,4}\b`
- Slovak IBAN: `\bSK\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}\b`

#### Mistral Service (`app/services/mistral.py`)
**Funkcie:**
- `generate_embedding(text)` - Vytvorí embedding pomocou `mistral-embed`
- `analyze_claim(claim_text, context, custom_prompt)` - AI analýza pomocou `mistral-small-latest`

### 6. Prompts System (`app/prompts.py`)

**Preddefinované prompty:**
1. **default** - Štandardná analýza
2. **detailed_medical** - Detailná zdravotná analýza s ICD-10 kódmi
3. **fraud_detection** - Detekcia podvodov
4. **quick_review** - Rýchle posúdenie
5. **slovak_language** - Analýza v slovenskom jazyku

**Placeholders:**
- `{context}` - Nahradí sa policy dokumentmi
- `{claim_text}` - Nahradí sa textom z claim

## Workflow celého systému

```
1. Upload PDF súborov
   ↓
2. Vytvorenie Claim + ClaimDocument záznamov
   ↓
3. Nahranie do S3
   ↓
4. Celery task: process_claim
   ├─ Presigned URL
   ├─ OCR (Mistral)
   ├─ Anonymizácia (Presidio)
   └─ Uloženie do DB
   ↓
5. Status: WAITING_FOR_APPROVAL
   ↓
6. Admin vyberie prompt a schváli
   ↓
7. Celery task: analyze_claim_task
   ├─ Agregácia textu
   ├─ AI analýza (Mistral)
   └─ Uloženie výsledku
   ↓
8. Status: ANALYZED
```

## Bezpečnosť a Privacy

1. **Anonymizácia pred AI** - Všetky citlivé údaje sú anonymizované pred odoslaním do Mistral AI
2. **Presigned URLs** - Dočasné odkazy na S3 súbory (1 hodina platnosť)
3. **Žiadne verejné S3 objekty** - Všetky súbory sú private
4. **Environment variables** - API kľúče a credentials v `.env` súbore

## Konfigurácia

**Environment variables (`.env`):**
```
MISTRAL_API_KEY=your_key
S3_ACCESS_KEY=your_key
S3_SECRET_KEY=your_secret
S3_BUCKET_NAME=ai-claims-docs
S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
S3_REGION=fr-par
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://redis:6379/0
```

## Škálovanie

**Aktuálne (PoC):**
- Všetko beží v Docker Compose na jednom VM
- 10 Celery workers (concurrent processing)

**Možnosti škálovania:**
- Horizontálne škálovanie workers (viacero VM s Celery)
- Managed PostgreSQL (Scaleway Database)
- Redis Cluster
- Load balancer pre backend
- CDN pre frontend
