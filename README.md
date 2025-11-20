# AI Claims Processing System

Inteligentný systém na spracovanie poistných udalostí s využitím AI, OCR, anonymizácie a analýzy dokumentov. Systém je nasadený na Scaleway infraštruktúre s podporou GDPR-compliant anonymizácie pomocou Microsoft Presidio.

## Prehľad

Tento systém automatizuje celý proces spracovania poistných udalostí od nahratia dokumentov až po AI-driven analýzu a generovanie reportov. Implementuje Human-in-the-Loop (HITL) v kritických bodoch procesu a zabezpečuje GDPR-compliant spracovanie citlivých dát.

### Hlavné Funkcie

- **OCR Spracovanie**: Automatická extrakcia textu z PDF dokumentov (Mistral AI)
- **Data Cleaning**: Pravidlové čistenie a normalizácia OCR výstupu
- **GDPR Anonymizácia**: Country-specific anonymizácia pomocou Microsoft Presidio
- **Human-in-the-Loop**: Manuálne kontrolné body pre OCR a anonymizáciu
- **AI Analýza**: RAG-enhanced analýza s Mistral AI a 5 preddefinovanými promptami
- **PDF Reporty**: Automatické generovanie structured PDF reportov
- **Audit Logging**: Kompletný audit trail všetkých zmien
- **Scaleway Integration**: Managed PostgreSQL + S3 Object Storage

## Architektúra

```
┌─────────────┐         ┌──────────────┐
│   Frontend  │────────▶│   Backend    │
│ (Streamlit) │         │  (FastAPI)   │
│ :8501       │         │  :8000       │
└─────────────┘         └──────┬───────┘
                               │
                ┌──────────────┼───────────────┐
                │              │               │
         ┌──────▼──────┐ ┌────▼─────┐  ┌─────▼──────┐
         │   Worker    │ │  Redis   │  │  Presidio  │
         │  (Celery)   │ │  :6379   │  │    API     │
         └──────┬──────┘ └──────────┘  │   :8001    │
                │                       └────────────┘
                │
    ┌───────────┴────────────┐
    │                        │
┌───▼────────────┐  ┌────────▼──────────┐
│  PostgreSQL    │  │  Scaleway S3      │
│  (Scaleway)    │  │  Object Storage   │
│  pgvector      │  │  (Documents)      │
└────────────────┘  └───────────────────┘
```

### Služby a Komunikácia

| Služba | Port | Popis | Komunikuje s |
|--------|------|-------|--------------|
| **Frontend** | 8501 | Streamlit UI | Backend API |
| **Backend** | 8000 | FastAPI REST API | Worker, PostgreSQL, S3, Frontend |
| **Worker** | - | Celery worker | Redis, PostgreSQL, S3, Presidio |
| **Redis** | 6379 | Message broker | Backend, Worker |
| **Presidio** | 8001 | Anonymization API | Worker |
| **PostgreSQL** | External | Scaleway Managed DB | Backend, Worker |
| **S3** | External | Scaleway Object Storage | Backend, Worker |

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM pre PostgreSQL
- **Celery** - Distributed task queue
- **Pydantic** - Data validation

### Frontend
- **Streamlit** - Interactive web UI

### AI & ML
- **Mistral AI** - OCR, Chat, Embeddings
- **Microsoft Presidio** - PII detection and anonymization
- **pgvector** - Vector similarity search pre RAG

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **PostgreSQL** - Scaleway Managed Database s pgvector
- **S3** - Scaleway Object Storage
- **Redis** - Celery message broker

### Libraries
- **ReportLab** - PDF generation
- **boto3** - S3 client
- **Requests** - HTTP client

## Workflow

```
1. Upload Documents (Frontend)
        ↓
2. OCR Processing (Mistral AI)
        ↓
3. OCR Review (HITL) ← Human validates/edits
        ↓
4. Data Cleaning (Rule-based)
        ↓
5. Anonymization (Presidio)
        ↓
6. Anonymization Review (HITL) ← Human validates/edits
        ↓
7. AI Analysis (Mistral + RAG)
        ↓
8. PDF Report Generation
        ↓
9. Download Report
```

### Stavy Claim

- `PROCESSING` - Nahrané dokumenty, prebieha OCR
- `OCR_REVIEW` - OCR dokončené, čaká na kontrolu
- `CLEANING` - Prebieha čistenie dát
- `ANONYMIZING` - Prebieha anonymizácia
- `ANONYMIZATION_REVIEW` - Anonymizácia dokončená, čaká na kontrolu
- `ANONYMIZED` - Anonymizácia schválená
- `READY_FOR_ANALYSIS` - Pripravené na AI analýzu
- `ANALYZING` - Prebieha AI analýza
- `ANALYZED` - Analýza dokončená, report vygenerovaný

## Štruktúra Projektu

```
ai-claims-scaleway-python/
├── app/
│   ├── core/
│   │   ├── config.py              # Pydantic settings
│   │   └── config_loader.py       # YAML config loader
│   ├── db/
│   │   ├── models.py              # SQLAlchemy models
│   │   └── session.py             # DB session
│   ├── services/
│   │   ├── storage.py             # S3 operations
│   │   ├── ocr.py                 # OCR service
│   │   ├── cleaner.py             # Data cleaning
│   │   ├── mistral.py             # Mistral AI client
│   │   ├── rag.py                 # RAG service
│   │   ├── report_generator.py    # PDF generation
│   │   └── audit.py               # Audit logging
│   ├── main.py                    # FastAPI app
│   └── worker.py                  # Celery tasks
├── frontend/
│   └── app.py                     # Streamlit UI
├── presidio-api/
│   ├── app.py                     # Presidio FastAPI wrapper
│   ├── requirements.txt
│   └── Dockerfile
├── config/
│   └── settings.yaml              # Centralized configuration
├── scripts/
│   └── migrate_db.py              # DB migration script
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Scaleway Account s:
  - Managed PostgreSQL database
  - Object Storage bucket
- Mistral AI API Key

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai-claims-scaleway-python
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in your credentials:
# - MISTRAL_API_KEY
# - DATABASE_URL (Scaleway PostgreSQL)
# - S3 credentials (Scaleway Object Storage)
```

### 3. Database Setup

Pripojte sa na Scaleway PostgreSQL a vytvorte `pgvector` extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Spustite migrácie:

```bash
python scripts/migrate_db.py
```

### 4. Start Services

```bash
docker-compose up -d
```

Služby budú dostupné na:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- Presidio API: http://localhost:8001

### 5. Initialize Prompts

Prompty sa automaticky načítajú z `config/settings.yaml` pri prvom spustení.

## Configuration (config/settings.yaml)

Centrálny konfiguračný súbor obsahuje:

### LLM Settings
```yaml
llm:
  analysis_model: mistral-small-latest
  embedding_model: mistral-embed
```

### Presidio Settings
```yaml
presidio:
  api_url: "http://presidio:8001"
  countries:
    SK:
      recognizers:
        - name: slovak_rc_pattern
          regex: '\b\d{6}[/]?\d{3,4}\b'
          score: 0.9
          entity_type: SK_RODNE_CISLO
      operators:
        PERSON: '<OSOBA>'
        PHONE_NUMBER: '<TELEFON>'
```

### Prompt Templates
```yaml
prompts:
  default:
    name: Štandardná analýza
    description: Základná analýza poistnej udalosti
    llm_model: mistral-small-latest
    template: |
      You are an expert insurance claim adjuster...
```

### RAG Settings
```yaml
rag:
  chunk_size: 1000
  chunk_overlap: 200
```

## API Endpoints

### Claims Management
- `POST /upload/` - Upload claim documents
- `GET /claims/` - List all claims
- `GET /claims/{claim_id}` - Get claim details
- `POST /claims/{claim_id}/retry-anonymization` - Retry stuck processing

### OCR Review (HITL)
- `GET /claims/{claim_id}/documents/{document_id}/ocr_review` - Get OCR text
- `POST /claims/{claim_id}/documents/{document_id}/ocr_review/approve` - Approve OCR
- `POST /claims/{claim_id}/documents/{document_id}/ocr_review/edit` - Edit and approve

### Anonymization Review (HITL)
- `GET /claims/{claim_id}/documents/{document_id}/anonymization_review` - Get anonymized text
- `POST /claims/{claim_id}/documents/{document_id}/anonymization_review/approve` - Approve
- `POST /claims/{claim_id}/documents/{document_id}/anonymization_review/edit` - Edit and approve

### Analysis
- `GET /prompts-config/` - List available prompts
- `POST /analyze/{claim_id}` - Start AI analysis

### Reports
- `GET /claims/{claim_id}/reports` - List reports
- `GET /claims/{claim_id}/reports/{report_id}/download` - Download PDF report

### RAG Management
- `GET /rag/categories` - List categories
- `POST /rag/upload` - Upload policy document
- `GET /rag/documents` - List RAG documents

### Audit
- `GET /audit_logs` - Get audit logs

## Frontend Pages

### 1. Nahlásenie udalosti
- Upload PDF dokumentov
- Výber krajiny (SK, IT, DE)
- Spustenie OCR

### 2. Admin Dashboard
- Prehľad všetkých claims
- Status monitoring
- Retry button pre zaseknuté claimy
- Prompt selection a spustenie analýzy
- Download PDF reportov

### 3. OCR Review
- Kontrola OCR výstupu
- Editácia textu
- Schvaľovanie dokumentov

### 4. Anonymization Review
- Kontrola anonymizovaného textu
- Editácia anonymizácie
- Schvaľovanie dokumentov

### 5. RAG Management
- Upload policy dokumentov
- Kategorizácia dokumentov
- Prehľad RAG dokumentov

### 6. Audit Logs
- Zobrazenie audit trail
- Filtrovanie podľa akcie/claim

## Data Storage

### PostgreSQL (Scaleway Managed)
- `claims` - Claim metadata, status, analysis results
- `claim_documents` - Document metadata, text content
- `analysis_reports` - Report metadata
- `rag_documents` - Policy documents + embeddings
- `prompt_templates` - Dynamic prompt storage
- `audit_logs` - Full audit trail

### S3 Object Storage (Scaleway)
- `claims/{claim_id}/originals/` - Original PDF documents
- `claims/{claim_id}/reports/` - Generated PDF reports
- `rag_documents/{category}/` - Policy documents

## Deployment to Scaleway

### 1. Create Managed PostgreSQL
```bash
# Scaleway Console -> Managed Databases -> PostgreSQL
# Create database, note connection details
```

### 2. Create Object Storage Bucket
```bash
# Scaleway Console -> Object Storage
# Create bucket, generate API keys
```

### 3. Configure Environment
Update `.env` with Scaleway credentials

### 4. Deploy with Docker Compose
```bash
docker-compose up -d
```

### 5. Setup Monitoring
- Check logs: `docker-compose logs -f`
- Monitor Celery: `docker-compose logs -f worker`

## Troubleshooting

### Worker Cannot Connect to Presidio
```bash
# Restart worker and presidio together
docker-compose restart worker presidio
```

### Claims Stuck in ANONYMIZING
Use the retry button in Admin Dashboard or API endpoint:
```bash
curl -X POST http://localhost:8000/claims/{claim_id}/retry-anonymization
```

### Database Connection Issues
Check DATABASE_URL format and credentials:
```bash
postgresql://username:password@host:port/database
```

### S3 Upload Fails
Verify S3 credentials and bucket permissions in Scaleway Console.

## Security

- All API keys stored in `.env` (not in git)
- `.env` is in `.gitignore`
- GDPR-compliant anonymization
- Audit logging for compliance
- HTTPS recommended for production

## License

Proprietary - All rights reserved

## Support

For issues and questions, contact the development team.
