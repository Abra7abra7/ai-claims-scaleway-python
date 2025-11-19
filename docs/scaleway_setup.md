# Scaleway Configuration Guide

To connect your application to Scaleway, you need to configure the `.env` file.

## 1. Database (PostgreSQL)

**For Local Development (PoC):**
You don't need to change anything! The project is configured to use a local Docker container for the database.
```ini
DATABASE_URL=postgresql://postgres:postgres@db:5432/claims_db
```

**For Production (Managed Database):**
If you want to use a real Scaleway Managed Database:
1. Go to [Scaleway Console > Managed Databases](https://console.scaleway.com/rdb/instances).
2. Create a PostgreSQL Instance.
3. Create a Database (e.g., `claims_db`) and a User (e.g., `claims_user`).
4. Copy the connection string and update `DATABASE_URL`.

## 2. Object Storage (S3)

This is **REQUIRED** for the AI processing to work.

1. **Create a Bucket**:
   - Go to [Object Storage](https://console.scaleway.com/object-storage/buckets).
   - Click "Create Bucket".
   - Name: e.g., `ai-claims-docs`.
   - Region: `fr-par` (Paris).
   - Visibility: Private.

2. **Get Credentials**:
   - Go to [IAM > API Keys](https://console.scaleway.com/iam/api-keys).
   - Click "Generate new API Key".
   - **Access Key**: Copy this to `S3_ACCESS_KEY`.
   - **Secret Key**: Copy this to `S3_SECRET_KEY` (Save it! You won't see it again).

3. **Update .env**:
   ```ini
   S3_ACCESS_KEY=SCWXXXXXXXXXXXXXXXXX
   S3_SECRET_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   S3_BUCKET_NAME=ai-claims-docs
   S3_REGION=fr-par
   S3_ENDPOINT_URL=https://s3.fr-par.scw.cloud
   ```

## 3. Mistral AI

1. Go to [Mistral AI Platform](https://console.mistral.ai/).
2. Generate an API Key.
3. Update `.env`:
   ```ini
   MISTRAL_API_KEY=your_mistral_api_key
   ```
