# 🏗️ AI Claims - Technical Architecture

**Last Updated:** December 9, 2024

This document provides a comprehensive technical overview of the AI Claims Processing System architecture, including all API endpoints, database models, services, and frontend components.

---

## 📑 Table of Contents

1. [System Overview](#system-overview)
2. [Backend Architecture](#backend-architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Pydantic Schemas](#pydantic-schemas)
6. [Services](#services)
7. [Frontend Architecture](#frontend-architecture)
8. [Docker Services](#docker-services)
9. [Data Flow](#data-flow)

---

## 🎯 System Overview

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 16, React 19, TypeScript 5, Tailwind CSS, shadcn/ui, next-intl |
| **Backend** | FastAPI 0.100+, Python 3.11+, Pydantic v2, SQLAlchemy 2.0 |
| **Database** | PostgreSQL 16 + pgvector extension |
| **Queue** | Redis 7 + Celery 5 |
| **Storage** | MinIO (S3-compatible) or Scaleway Object Storage |
| **AI Services** | Mistral AI, Google Gemini, OpenAI, Microsoft Presidio |
| **Deployment** | Docker + Docker Compose |

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                             │
│                       (Next.js 16, React 19)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────────┐ │
│  │ Dashboard  │  │  Claims    │  │  Settings  │  │   Admin     │ │
│  │  (Stats)   │  │  (CRUD)    │  │  (User)    │  │   (Mgmt)    │ │
│  └────────────┘  └────────────┘  └────────────┘  └─────────────┘ │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │         shadcn/ui Components + Tailwind CSS                │   │
│  │   Type-safe API Client (openapi-fetch + react-query)      │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬───────────────────────────────────┘
                                 │ HTTPS REST API (JSON)
                                 ↓
┌────────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                              │
│                       (FastAPI + SQLAlchemy)                       │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  API Router (/api/v1)                                      │   │
│  │  ├─ /auth       - Authentication (12 endpoints)           │   │
│  │  ├─ /claims     - Claims CRUD (8 endpoints)               │   │
│  │  ├─ /ocr        - OCR review (3 endpoints)                │   │
│  │  ├─ /anonymization - Anon review (3 endpoints)            │   │
│  │  ├─ /analysis   - AI analysis (4 endpoints)               │   │
│  │  ├─ /rag        - Policy docs (6 endpoints)               │   │
│  │  ├─ /reports    - Report mgmt (3 endpoints)               │   │
│  │  ├─ /audit      - Audit logs (3 endpoints)                │   │
│  │  ├─ /prompts    - Prompt mgmt (2 endpoints)               │   │
│  │  ├─ /stats      - Statistics (3 endpoints)                │   │
│  │  └─ /health     - Health checks (3 endpoints)             │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  Services Layer                                            │   │
│  │  ├─ AuthService      - User auth + sessions               │   │
│  │  ├─ EmailService     - SMTP email sending                 │   │
│  │  ├─ TokenService     - Email/reset token mgmt             │   │
│  │  ├─ StorageService   - S3/MinIO file storage              │   │
│  │  ├─ RAGService       - Vector search + embeddings         │   │
│  │  ├─ AuditLogger      - Audit trail logging                │   │
│  │  └─ WorkerTasks      - Celery background tasks            │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────┬─────────────────┬────────────────┬──────────────────────┘
           │                 │                │
           ↓                 ↓                ↓
┌──────────────────┐  ┌──────────────┐  ┌────────────────┐
│   PostgreSQL     │  │    Redis     │  │  Presidio API  │
│   + pgvector     │  │   (Queue)    │  │  (PII Detect)  │
│                  │  │              │  │                │
│  8 Tables:       │  │  - Celery    │  │  - Country-    │
│  - users         │  │  - Cache     │  │    specific    │
│  - user_sessions │  │              │  │  - SK, IT, DE  │
│  - auth_tokens   │  └──────┬───────┘  └────────────────┘
│  - claims        │         │
│  - documents     │         ↓
│  - rag_docs      │  ┌──────────────┐
│  - audit_logs    │  │   Worker     │
│  - reports       │  │  (Celery)    │
│  - prompts       │  │              │
└────────┬─────────┘  │  Background  │
         │            │  Tasks:      │
         │            │  - OCR       │
         │            │  - Cleaning  │
         │            │  - Anon      │
         │            │  - Analysis  │
         │            │  - Emails    │
         │            └──────────────┘
         ↓
┌─────────────────────────────────────────┐
│        MinIO / S3 Storage               │
│                                         │
│  Buckets:                               │
│  - ai-claims/                           │
│    ├─ claims/{id}/                      │
│    │  ├─ original/                      │
│    │  ├─ processed/                     │
│    │  └─ reports/                       │
│    └─ rag/                              │
│       └─ {country}/{type}/              │
└─────────────────────────────────────────┘
```

---

## 🔧 Backend Architecture

### Project Structure

```
app/
├── main.py                    # FastAPI application entry point
├── core/
│   ├── config.py              # Settings (Pydantic BaseSettings)
│   └── security.py            # Password hashing utilities
├── db/
│   ├── models.py              # SQLAlchemy ORM models
│   └── database.py            # Database session management
├── api/
│   ├── deps.py                # Common dependencies (get_db, get_current_user)
│   └── v1/
│       ├── router.py          # Main API router aggregation
│       ├── endpoints/         # API endpoint handlers (11 files)
│       │   ├── auth.py
│       │   ├── claims.py
│       │   ├── ocr.py
│       │   ├── anonymization.py
│       │   ├── analysis.py
│       │   ├── rag.py
│       │   ├── reports.py
│       │   ├── audit.py
│       │   ├── prompts.py
│       │   ├── stats.py
│       │   └── health.py
│       └── schemas/           # Pydantic request/response schemas (9 files)
│           ├── auth.py
│           ├── claims.py
│           ├── documents.py
│           ├── ocr.py
│           ├── anonymization.py
│           ├── analysis.py
│           ├── rag.py
│           ├── reports.py
│           ├── audit.py
│           ├── prompts.py
│           └── base.py
├── services/
│   ├── auth.py                # Authentication business logic
│   ├── email_service.py       # Email sending (SMTP)
│   ├── token_service.py       # Token generation/validation
│   ├── storage.py             # S3/MinIO file operations
│   ├── rag.py                 # Vector search + embeddings
│   ├── audit.py               # Audit logging
│   └── worker_tasks.py        # Celery tasks (OCR, analysis, etc.)
└── prompts/
    └── __init__.py            # Prompt templates for AI analysis
```

### Key Design Patterns

- **Repository Pattern**: Service layer abstracts database operations
- **Dependency Injection**: FastAPI's `Depends()` for clean dependencies
- **Schema Validation**: Pydantic for all request/response validation
- **Type Safety**: Full Python type hints throughout
- **OpenAPI**: Auto-generated API documentation at `/api/v1/docs`

---

## 🗄️ Database Schema

### PostgreSQL Tables

#### 1. `users` - User Accounts

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | User ID |
| `email` | VARCHAR UNIQUE | User email (login) |
| `password_hash` | VARCHAR | PBKDF2-SHA256 hashed password |
| `name` | VARCHAR | Full name |
| `role` | VARCHAR | admin, user, viewer |
| `locale` | VARCHAR | Preferred language (sk, en) |
| `is_active` | BOOLEAN | Account enabled/disabled |
| `email_verified` | BOOLEAN | Email verification status |
| `created_at` | TIMESTAMP | Registration date |
| `updated_at` | TIMESTAMP | Last profile update |
| `last_login_at` | TIMESTAMP | Last successful login |

**Indexes:**
- `idx_users_email` - Fast email lookup for login

#### 2. `user_sessions` - Active Sessions

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Session ID |
| `user_id` | INTEGER FK → users.id | Owner user |
| `token` | VARCHAR UNIQUE | Random session token |
| `ip_address` | VARCHAR | Client IP address |
| `user_agent` | VARCHAR | Browser/client info |
| `created_at` | TIMESTAMP | Session start |
| `expires_at` | TIMESTAMP | Session expiry (7 days) |
| `last_activity_at` | TIMESTAMP | Last API call |
| `is_revoked` | BOOLEAN | Manually revoked? |
| `revoked_at` | TIMESTAMP | When revoked |
| `revoked_reason` | VARCHAR | Logout, password change, etc. |

**Indexes:**
- `idx_sessions_token` - Fast token lookup
- `idx_sessions_user_id` - List user's sessions

#### 3. `auth_tokens` - Email/Reset Tokens

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Token ID |
| `token` | VARCHAR UNIQUE | Random secure token |
| `token_type` | VARCHAR | email_verification, password_reset |
| `user_email` | VARCHAR | Associated user |
| `expires_at` | TIMESTAMP | Token expiry |
| `used` | BOOLEAN | Already consumed? |
| `created_at` | TIMESTAMP | Token generation |

**Indexes:**
- `idx_auth_tokens_token` - Fast token validation
- `idx_auth_tokens_user_email` - List user's tokens

#### 4. `claims` - Insurance Claims

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Claim ID |
| `country` | VARCHAR | SK, IT, DE |
| `status` | VARCHAR | PROCESSING, OCR_REVIEW, ... |
| `analysis_result` | JSONB | AI analysis output |
| `analysis_model` | VARCHAR | Model used for analysis |
| `created_at` | TIMESTAMP | Upload time |

**Statuses:**
- `PROCESSING` - Initial upload
- `OCR_REVIEW` - Needs human OCR review
- `CLEANING` - Data cleaning in progress
- `ANONYMIZING` - PII anonymization in progress
- `ANONYMIZATION_REVIEW` - Needs human anon review
- `READY_FOR_ANALYSIS` - Ready for AI analysis
- `ANALYZING` - AI analysis in progress
- `ANALYZED` - Analysis complete
- `FAILED` - Error occurred

#### 5. `claim_documents` - Uploaded Files

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Document ID |
| `claim_id` | INTEGER FK → claims.id | Parent claim |
| `filename` | VARCHAR | Original filename |
| `s3_key` | VARCHAR | MinIO/S3 object key |
| `original_text` | TEXT | OCR extracted text |
| `cleaned_text` | TEXT | After cleaning |
| `anonymized_text` | TEXT | After anonymization |
| `embedding` | VECTOR(1024) | Text embedding for RAG |
| `ocr_reviewed_by` | VARCHAR | User who reviewed OCR |
| `ocr_reviewed_at` | TIMESTAMP | OCR review time |
| `anon_reviewed_by` | VARCHAR | User who reviewed anon |
| `anon_reviewed_at` | TIMESTAMP | Anon review time |

**pgvector Extension:**
- `embedding` column stores 1024-dim vectors for semantic search

#### 6. `rag_documents` - Policy Documents

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Document ID |
| `filename` | VARCHAR | Original filename |
| `s3_key` | VARCHAR | MinIO/S3 object key |
| `country` | VARCHAR | SK, IT, DE |
| `document_type` | VARCHAR | general, health, vehicle, property, liability |
| `text_content` | TEXT | Extracted text |
| `embedding` | VECTOR(1024) | Text embedding |
| `uploaded_by` | VARCHAR | Admin who uploaded |
| `created_at` | TIMESTAMP | Upload time |

#### 7. `audit_logs` - Audit Trail

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Log ID |
| `user` | VARCHAR | User email |
| `action` | VARCHAR | Action type (see below) |
| `entity_type` | VARCHAR | Claim, User, RAGDocument, etc. |
| `entity_id` | INTEGER | Affected entity ID |
| `changes` | JSONB | What changed |
| `timestamp` | TIMESTAMP | When it happened |

**Audit Actions:**
- **Auth:** `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`, `REGISTER_SUCCESS`, `EMAIL_VERIFIED`, `PASSWORD_CHANGED`, `PASSWORD_RESET_REQUESTED`, `PASSWORD_RESET_COMPLETED`, `SESSION_REVOKED`, `ALL_SESSIONS_REVOKED`
- **Claims:** `CLAIM_CREATED`, `CLAIM_UPDATED`, `CLAIM_DELETED`, `CLAIM_STATUS_CHANGED`
- **OCR:** `OCR_EDITED`, `OCR_APPROVED`, `OCR_REJECTED`
- **Anonymization:** `ANON_EDITED`, `ANON_APPROVED`, `ANON_REJECTED`
- **Analysis:** `ANALYSIS_STARTED`, `ANALYSIS_COMPLETED`
- **RAG:** `RAG_DOCUMENT_UPLOADED`, `RAG_DOCUMENT_DELETED`
- **Reports:** `REPORT_GENERATED`

#### 8. `analysis_reports` - Generated Reports

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Report ID |
| `claim_id` | INTEGER FK → claims.id | Parent claim |
| `s3_key` | VARCHAR | MinIO/S3 PDF key |
| `model_used` | VARCHAR | LLM model |
| `prompt_id` | VARCHAR | Prompt template ID |
| `created_at` | TIMESTAMP | Generation time |

#### 9. `prompt_templates` - AI Prompts

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PRIMARY KEY | Template ID |
| `name` | VARCHAR UNIQUE | Prompt name |
| `description` | VARCHAR | Human-readable description |
| `template` | TEXT | Prompt template |
| `llm_model` | VARCHAR | Default model |
| `created_at` | TIMESTAMP | Creation time |

### Database Relationships

```
users 1──── ∞ user_sessions
users 1──── ∞ auth_tokens (via email)

claims 1──── ∞ claim_documents
claims 1──── ∞ analysis_reports

(audit_logs references all entities but no FK)
```

---

## 🔌 API Endpoints

### Authentication (`/api/v1/auth/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | Login with email/password | No |
| POST | `/logout` | Logout current session | Yes |
| GET | `/me` | Get current user info | Yes |
| GET | `/sessions` | List user's active sessions | Yes |
| DELETE | `/sessions/{id}` | Revoke specific session | Yes |
| DELETE | `/sessions` | Revoke all other sessions | Yes |
| POST | `/password/change` | Change password (old + new) | Yes |
| POST | `/password-reset/request` | Request password reset email | No |
| POST | `/password-reset/confirm` | Confirm reset with token | No |
| POST | `/verify-email/send` | Resend verification email | No |
| GET | `/verify-email/{token}` | Verify email with token | No |
| GET | `/users` | List all users (admin) | Admin |
| PUT | `/users/{id}/status` | Enable/disable user (admin) | Admin |

### Claims (`/api/v1/claims/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List all claims (paginated) | Yes |
| GET | `/{id}` | Get claim details | Yes |
| POST | `/` | Create new claim + upload PDF | Yes |
| PUT | `/{id}` | Update claim metadata | Yes |
| DELETE | `/{id}` | Delete claim (+ cascade) | Yes |
| POST | `/{id}/start-ocr` | Trigger OCR processing | Yes |
| POST | `/{id}/start-anonymization` | Trigger anonymization | Yes |
| POST | `/{id}/start-analysis` | Trigger AI analysis | Yes |

### OCR Review (`/api/v1/ocr/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/{claim_id}` | Get OCR text for review | Yes |
| PUT | `/{claim_id}` | Update OCR text | Yes |
| POST | `/{claim_id}/approve` | Approve OCR, move to next step | Yes |

### Anonymization Review (`/api/v1/anonymization/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/{claim_id}` | Get cleaned + anonymized texts | Yes |
| PUT | `/{claim_id}` | Update anonymized text | Yes |
| POST | `/{claim_id}/approve` | Approve anon, ready for analysis | Yes |

### Analysis (`/api/v1/analysis/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/{claim_id}` | Start AI analysis with prompt | Yes |
| GET | `/{claim_id}` | Get analysis result | Yes |
| POST | `/{claim_id}/regenerate` | Re-run analysis | Yes |
| GET | `/{claim_id}/history` | Get analysis history | Yes |

### RAG Documents (`/api/v1/rag/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/documents` | List RAG documents (filter by country/type) | Yes |
| GET | `/structure` | Get folder structure (countries → types → counts) | Yes |
| POST | `/upload` | Upload new policy document | Admin |
| DELETE | `/{id}` | Delete policy document | Admin |
| GET | `/{id}` | Get document details | Yes |
| GET | `/search` | Semantic search in policies | Yes |

### Reports (`/api/v1/reports/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/{claim_id}` | List reports for claim | Yes |
| GET | `/{claim_id}/{report_id}` | Download specific report (PDF) | Yes |
| POST | `/{claim_id}/regenerate` | Regenerate report | Yes |

### Audit Logs (`/api/v1/audit/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List all audit logs (admin) | Admin |
| GET | `/claims/{id}` | Get audit trail for claim | Yes |
| GET | `/actions` | Get available action types | Yes |

### Prompts (`/api/v1/prompts/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List available prompts | Yes |
| GET | `/config` | Get prompt configuration from YAML | Yes |

### Statistics (`/api/v1/stats/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/dashboard` | Get dashboard stats (claims by status, country) | Yes |
| GET | `/claims/by-status` | Claims grouped by status | Yes |
| GET | `/claims/by-country` | Claims grouped by country | Yes |

### Health (`/api/v1/health/*`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Health check (DB, Redis, Presidio) | No |
| GET | `/ready` | Readiness check | No |
| GET | `/live` | Liveness check | No |

**Total:** 50+ REST API endpoints

---

## 📦 Pydantic Schemas

### Authentication Schemas (`app/api/v1/schemas/auth.py`)

```python
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str  # min 8 chars
    name: str
    locale: str = "sk"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    locale: str
    is_active: bool
    email_verified: bool
    created_at: datetime

class SessionResponse(BaseModel):
    id: int
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_activity_at: datetime
    is_current: bool

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class MessageResponse(BaseModel):
    message: str
```

### Claims Schemas (`app/api/v1/schemas/claims.py`)

```python
class ClaimSummary(BaseModel):
    id: int
    country: str
    status: str
    document_count: int
    created_at: datetime

class ClaimListResponse(BaseModel):
    items: list[ClaimSummary]
    total: int
    skip: int
    limit: int

class ClaimDetail(BaseModel):
    id: int
    country: str
    status: str
    created_at: datetime
    documents: list[DocumentSummary]
    analysis_result: dict | None
    reports: list[ReportSummary]

class ClaimUploadResponse(BaseModel):
    claim_id: int
    document_id: int
    filename: str
    status: str
```

### Base Schemas (`app/api/v1/schemas/base.py`)

```python
class Country(str, Enum):
    SK = "SK"
    IT = "IT"
    DE = "DE"

class ClaimStatus(str, Enum):
    PROCESSING = "PROCESSING"
    OCR_REVIEW = "OCR_REVIEW"
    ANONYMIZATION_REVIEW = "ANONYMIZATION_REVIEW"
    READY_FOR_ANALYSIS = "READY_FOR_ANALYSIS"
    ANALYZING = "ANALYZING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"

class RAGDocumentType(str, Enum):
    GENERAL = "general"
    HEALTH = "health"
    VEHICLE = "vehicle"
    PROPERTY = "property"
    LIABILITY = "liability"

class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    services: dict[str, str]
```

---

## 🔧 Services

### 1. AuthService (`app/services/auth.py`)

**Purpose:** Handles all authentication logic

**Methods:**
- `authenticate_user(db, email, password)` - Verify credentials
- `create_user(db, email, password, name)` - Register new user
- `create_session(db, user, request)` - Create session token
- `get_user_by_session(db, token)` - Validate session
- `revoke_session(db, session_id, reason)` - Logout
- `revoke_all_sessions(db, user_id, except_current)` - Logout everywhere
- `change_password(db, user, old_pass, new_pass)` - Update password
- `reset_password(db, user, new_password)` - Reset without old password
- `_log_auth_action(db, action, user_email, details)` - Audit logging

**Security Features:**
- PBKDF2-SHA256 password hashing (100k iterations)
- Cryptographically secure random tokens (32 bytes)
- Session expiry (7 days default)
- IP address + User-Agent tracking
- Automatic email verification on password reset

### 2. EmailService (`app/services/email_service.py`)

**Purpose:** Send transactional emails via SMTP

**Methods:**
- `send_verification_email(to_email, token, user_name)` - Email verification
- `send_password_reset_email(to_email, token, user_name)` - Password reset
- `_send_email(to_email, subject, html_body)` - Internal SMTP sender

**Templates:**
- HTML email templates with inline CSS
- Branded with company colors
- Mobile-responsive

**Configuration:**
- SMTP host/port from `.env`
- Support for Gmail App Passwords
- TLS encryption enabled

### 3. TokenService (`app/services/token_service.py`)

**Purpose:** Manage one-time tokens for email flows

**Methods:**
- `create_email_verification_token(email, db, expires_in_hours=24)` - Generate verification token
- `create_password_reset_token(email, db, expires_in_hours=1)` - Generate reset token
- `validate_token(token, expected_type, db)` - Check if valid
- `mark_token_used(token, db)` - Invalidate after use
- `cleanup_expired_tokens(db)` - Remove expired tokens

**Token Properties:**
- Cryptographically random (32 bytes, URL-safe)
- Single-use only (`used = TRUE` after consumption)
- Time-limited expiration
- Type-specific validation

### 4. StorageService (`app/services/storage.py`)

**Purpose:** S3/MinIO file operations

**Methods:**
- `upload_file(file, claim_id, file_type)` - Upload PDF/document
- `download_file(s3_key)` - Download file
- `delete_file(s3_key)` - Delete file
- `generate_presigned_url(s3_key, expires_in=3600)` - Temporary download URL

**Bucket Structure:**
```
ai-claims/
├─ claims/{claim_id}/
│  ├─ original/{filename}
│  ├─ processed/{filename}
│  └─ reports/{report_id}.pdf
└─ rag/
   └─ {country}/{type}/{filename}
```

### 5. RAGService (`app/services/rag.py`)

**Purpose:** Vector search and RAG document management

**Methods:**
- `list_documents(db, country, document_type, limit, offset)` - List policy docs
- `get_folder_structure(db)` - Get hierarchical structure
- `upload_document(db, file, country, doc_type, user)` - Upload policy
- `delete_document(db, doc_id)` - Delete policy
- `search_similar(db, query, country, top_k=5)` - Semantic search
- `_generate_embedding(text)` - Create vector embedding

**Vector Search:**
- Uses pgvector extension
- 1024-dimension embeddings
- Cosine similarity search
- Country-specific filtering

### 6. AuditLogger (`app/services/audit.py`)

**Purpose:** Comprehensive audit trail

**Methods:**
- `log_action(user, action, entity_type, entity_id, changes, db)` - Log any action
- `get_audit_trail(entity_type, entity_id, db)` - Get history for entity
- `get_all_logs(skip, limit, db)` - List all logs (admin)

**Logged Information:**
- Who (user email)
- What (action type)
- When (timestamp)
- Where (entity type + ID)
- Changes (old vs new values in JSON)

### 7. WorkerTasks (`app/services/worker_tasks.py`)

**Purpose:** Celery background tasks

**Tasks:**
- `ocr_extract_text(claim_id, document_id)` - Call Mistral AI OCR
- `clean_text(claim_id, document_id)` - Remove OCR artifacts
- `anonymize_text(claim_id, document_id)` - Call Presidio API
- `analyze_claim(claim_id, prompt_id)` - LLM analysis with RAG
- `generate_report_pdf(claim_id, analysis_id)` - Create PDF report
- `send_email_task(to, subject, body)` - Async email sending

**Task Patterns:**
- Retry on failure (3 attempts)
- Exponential backoff
- Status updates in DB
- Error logging

---

## 🎨 Frontend Architecture

### Project Structure

```
frontend/src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout (providers, fonts)
│   ├── page.tsx                  # Dashboard homepage
│   │
│   ├── auth/                     # Authentication pages
│   │   ├── sign-in/page.tsx
│   │   ├── sign-up/page.tsx
│   │   ├── forgot-password/page.tsx
│   │   ├── reset-password/page.tsx
│   │   └── verify-email/page.tsx
│   │
│   ├── claims/                   # Claims management
│   │   ├── page.tsx              # List all claims
│   │   ├── new/page.tsx          # Upload new claim
│   │   └── [id]/                 # Claim detail
│   │       ├── page.tsx          # Overview
│   │       ├── ocr/page.tsx      # OCR review
│   │       ├── anon/page.tsx     # Anonymization review
│   │       └── analysis/page.tsx # AI analysis
│   │
│   ├── rag/page.tsx              # RAG documents
│   ├── reports/page.tsx          # Report list
│   ├── audit/page.tsx            # Audit log (admin)
│   │
│   ├── settings/                 # User settings
│   │   ├── page.tsx              # Profile + password change
│   │   └── sessions/page.tsx     # Session management
│   │
│   └── admin/                    # Admin section
│       └── users/page.tsx        # User management
│
├── components/                   # React components
│   ├── ui/                       # shadcn/ui components (30+ components)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   └── ... (and more)
│   │
│   ├── layout/                   # Layout components
│   │   ├── sidebar.tsx           # Left navigation menu
│   │   ├── app-layout.tsx        # Main app wrapper
│   │   └── header.tsx
│   │
│   ├── claims/                   # Claims-specific components
│   │   ├── claims-list.tsx
│   │   ├── claim-detail.tsx
│   │   └── claim-upload.tsx
│   │
│   └── dashboard/                # Dashboard components
│       └── dashboard-content.tsx
│
├── lib/                          # Utilities
│   ├── api-types.ts              # Auto-generated from OpenAPI (3700+ lines)
│   ├── types.ts                  # Helper type exports
│   ├── api.ts                    # Type-safe API client
│   ├── auth-client.ts            # Auth utilities (login, logout, etc.)
│   └── utils.ts                  # Misc helpers (cn(), etc.)
│
├── messages/                     # Translations
│   ├── sk.json                   # Slovak translations
│   └── en.json                   # English translations
│
└── i18n/
    └── request.ts                # next-intl config
```

### Type-Safe API Client

**File:** `frontend/src/lib/api.ts`

```typescript
import createClient from "openapi-fetch";
import type { paths } from "./api-types";

const client = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  credentials: "include", // Include cookies
});

export const api = client;
```

**Usage Example:**

```typescript
import { api } from "@/lib/api";

// Type-safe GET request
const { data, error } = await api.GET("/api/v1/claims");
// data is typed as ClaimListResponse
// error is typed as ErrorResponse

// Type-safe POST request
const { data, error } = await api.POST("/api/v1/claims", {
  body: {
    country: "SK",
    // TypeScript knows all required fields!
  }
});
```

### React Query Integration

**File:** `frontend/src/lib/api.ts`

```typescript
import { useQuery, useMutation } from "@tanstack/react-query";

// Custom hooks for common operations
export const useClaims = () => {
  return useQuery({
    queryKey: ["claims"],
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/claims");
      if (error) throw error;
      return data;
    },
  });
};

export const useCreateClaim = () => {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const { data, error } = await api.POST("/api/v1/claims", {
        body: formData,
      });
      if (error) throw error;
      return data;
    },
  });
};
```

### Internationalization

**Supported Languages:** Slovak (sk), English (en)

**Structure:**

```json
// messages/sk.json
{
  "nav": {
    "dashboard": "Dashboard",
    "claims": "Poistné udalosti",
    "rag": "Dokumenty",
    "settings": "Nastavenia"
  },
  "claims": {
    "title": "Poistné udalosti",
    "upload": "Nahrať dokument",
    "status": {
      "PROCESSING": "Spracováva sa",
      "OCR_REVIEW": "OCR kontrola"
    }
  }
}
```

**Usage:**

```tsx
import { useTranslations } from "next-intl";

export default function ClaimsPage() {
  const t = useTranslations("claims");
  
  return <h1>{t("title")}</h1>; // "Poistné udalosti"
}
```

---

## 🐳 Docker Services

### Service Breakdown

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **frontend** | node:20-alpine | 3000 | Next.js UI |
| **backend** | python:3.11-slim | 8000 | FastAPI API |
| **worker** | python:3.11-slim | - | Celery tasks |
| **db** | pgvector/pgvector:pg16 | 5432 | PostgreSQL + pgvector |
| **redis** | redis:7-alpine | 6379 | Queue + cache |
| **minio** | minio/minio:latest | 9000, 9001 | S3-compatible storage |
| **presidio** | Custom (Dockerfile.presidio) | 8001 | PII detection API |

### docker-compose.yml Configuration

```yaml
version: "3.9"

services:
  # Frontend - Next.js
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  # Backend - FastAPI
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://claims_user:claims_password@db:5432/claims_db
      - REDIS_URL=redis://redis:6379
      - S3_ENDPOINT_URL=http://minio:9000
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FRONTEND_URL=${FRONTEND_URL}
    volumes:
      - ./app:/app/app
    depends_on:
      - db
      - redis
      - minio
      - presidio
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Worker - Celery
  worker:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://claims_user:claims_password@db:5432/claims_db
      - REDIS_URL=redis://redis:6379
      - S3_ENDPOINT_URL=http://minio:9000
      - MISTRAL_API_KEY=${MISTRAL_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - ./app:/app/app
    depends_on:
      - db
      - redis
    command: celery -A app.services.worker_tasks worker --loglevel=info

  # Database - PostgreSQL + pgvector
  db:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=claims_user
      - POSTGRES_PASSWORD=claims_password
      - POSTGRES_DB=claims_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U claims_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis - Queue + Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # MinIO - S3-compatible storage
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

  # Presidio - PII Detection
  presidio:
    build:
      context: ./presidio-api
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  minio_data:
```

---

## 🔄 Data Flow

### Complete Claim Processing Flow

```
1. USER: Upload PDF
   └─> POST /api/v1/claims (multipart/form-data)
       └─> Backend: Create claim record
           └─> StorageService: Upload to MinIO
               └─> Celery: Queue OCR task
                   └─> Database: status = "PROCESSING"
                   └─> Response: {"claim_id": 123, "status": "PROCESSING"}

2. WORKER: OCR Processing
   └─> Celery task: ocr_extract_text(claim_id=123)
       └─> Mistral AI: POST /v1/files (PDF)
           └─> Mistral AI: POST /v1/batch (extraction job)
               └─> Wait for completion
                   └─> Database: original_text = extracted_text
                       └─> Database: status = "OCR_REVIEW"

3. USER: OCR Review
   └─> GET /api/v1/ocr/123
       └─> Response: {"claim_id": 123, "text": "..."}
   └─> Frontend: User edits text
   └─> PUT /api/v1/ocr/123 (edited text)
       └─> AuditLogger: log "OCR_EDITED"
   └─> POST /api/v1/ocr/123/approve
       └─> Database: ocr_reviewed_by = user.email
           └─> Database: status = "CLEANING"
           └─> Celery: Queue cleaning task

4. WORKER: Data Cleaning
   └─> Celery task: clean_text(claim_id=123)
       └─> Apply regex rules (remove OCR artifacts)
           └─> Database: cleaned_text = cleaned
               └─> Database: status = "ANONYMIZING"
               └─> Celery: Queue anonymization task

5. WORKER: Anonymization
   └─> Celery task: anonymize_text(claim_id=123)
       └─> POST http://presidio:8001/anonymize
           └─> Presidio: Detect PII (country-specific)
               └─> Presidio: Mask entities
                   └─> Database: anonymized_text = anonymized
                       └─> Database: status = "ANONYMIZATION_REVIEW"

6. USER: Anonymization Review
   └─> GET /api/v1/anonymization/123
       └─> Response: {"cleaned": "...", "anonymized": "..."}
   └─> Frontend: Side-by-side comparison
   └─> POST /api/v1/anonymization/123/approve
       └─> Database: anon_reviewed_by = user.email
           └─> Database: status = "READY_FOR_ANALYSIS"

7. USER: Start AI Analysis
   └─> POST /api/v1/analysis/123 {"prompt_id": "default"}
       └─> Database: status = "ANALYZING"
           └─> Celery: Queue analysis task

8. WORKER: AI Analysis
   └─> Celery task: analyze_claim(claim_id=123, prompt_id="default")
       └─> RAGService: search_similar(query, country="SK", top_k=5)
           └─> pgvector: Cosine similarity search
               └─> Top 5 policy documents
       └─> Build context: anonymized_text + RAG documents
       └─> LLM API: POST (Mistral/Gemini/OpenAI)
           └─> Structured response extraction
               └─> Database: analysis_result = {...}
                   └─> Database: status = "ANALYZED"
                   └─> Celery: Queue PDF generation

9. WORKER: Report Generation
   └─> Celery task: generate_report_pdf(claim_id=123)
       └─> ReportLib: Build PDF from analysis_result
           └─> StorageService: Upload to MinIO
               └─> Database: Insert analysis_reports record
                   └─> AuditLogger: log "REPORT_GENERATED"

10. USER: Download Report
    └─> GET /api/v1/reports/123
        └─> Response: [{"id": 1, "created_at": "..."}]
    └─> GET /api/v1/reports/123/1
        └─> StorageService: Generate presigned URL
            └─> Response: redirect to MinIO URL
                └─> User downloads PDF
```

### Authentication Flow

```
REGISTRATION:
1. POST /api/v1/auth/register {"email": "user@example.com", "password": "..."}
   └─> AuthService: create_user(...)
       └─> Hash password (PBKDF2-SHA256)
       └─> Database: Insert user (email_verified = FALSE)
       └─> TokenService: create_email_verification_token(...)
           └─> EmailService: send_verification_email(...)
               └─> SMTP: Send email with token link
   └─> Response: {"id": 1, "email": "...", "email_verified": false}
   └─> Frontend: Redirect to /auth/sign-in

2. User clicks link: GET /api/v1/auth/verify-email/{token}
   └─> TokenService: validate_token(token, "email_verification")
       └─> Database: email_verified = TRUE
       └─> AuditLogger: log "EMAIL_VERIFIED"
   └─> Response: redirect to /auth/sign-in?verified=true

LOGIN:
3. POST /api/v1/auth/login {"email": "...", "password": "..."}
   └─> AuthService: authenticate_user(...)
       └─> Check email_verified = TRUE
       └─> Verify password hash
       └─> AuthService: create_session(...)
           └─> Generate random token (32 bytes)
           └─> Database: Insert user_sessions
           └─> Set HTTP-only cookie: session_token=...
           └─> AuditLogger: log "LOGIN_SUCCESS" + IP + User-Agent
   └─> Response: {"user": {...}, "token": "..."}

API REQUEST:
4. GET /api/v1/claims (Cookie: session_token=...)
   └─> Dependency: get_current_user(session_token)
       └─> Database: Query user_sessions WHERE token=...
           └─> Check expires_at > now()
           └─> Check is_revoked = FALSE
           └─> Database: Load user
           └─> Update last_activity_at
   └─> Endpoint: List claims for user
   └─> Response: {"items": [...]}

LOGOUT:
5. POST /api/v1/auth/logout
   └─> AuthService: revoke_session(session_id, reason="LOGOUT")
       └─> Database: UPDATE user_sessions SET is_revoked=TRUE
       └─> AuditLogger: log "LOGOUT"
       └─> Clear cookie
   └─> Response: {"message": "Logged out"}
```

---

## 📝 Notes

### Environment Variables

**Critical:**
- Never commit `.env` to Git
- Use `.env.example` for templates
- Production secrets in secure vault

**Required for Development:**
```bash
DATABASE_URL=postgresql://...
MISTRAL_API_KEY=...
SMTP_HOST=smtp.gmail.com
SMTP_USER=...
SMTP_PASSWORD=...  # Gmail App Password
```

### Type Generation

**Automatic:**
- Git pre-commit hook generates types from OpenAPI
- `frontend/src/lib/api-types.ts` is auto-generated
- **DO NOT edit manually**

**Manual:**
```bash
cd frontend
npm run generate-types
```

### Deployment

**Local Development:**
```bash
docker-compose up -d
```

**Production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

**Last Updated:** December 9, 2024  
**Version:** 1.0

