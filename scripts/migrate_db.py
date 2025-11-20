#!/usr/bin/env python3
"""
Database migration script for AI Claims Processing System.
Adds new columns and tables for the enhanced workflow.

Usage:
    python scripts/migrate_db.py
"""

from sqlalchemy import create_engine, text
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import get_settings
from app.db.models import Base
from app.db.session import engine

def run_migrations():
    """Run database migrations"""
    print("Starting database migrations...")
    
    with engine.connect() as connection:
        # Ensure vector extension is enabled
        print("Ensuring pgvector extension...")
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
        
        # Add new columns to existing tables (if they don't exist)
        print("Adding new columns to claims table...")
        try:
            connection.execute(text("""
                ALTER TABLE claims 
                ADD COLUMN IF NOT EXISTS country VARCHAR(10) DEFAULT 'SK',
                ADD COLUMN IF NOT EXISTS analysis_model VARCHAR(255)
            """))
            connection.commit()
            print("✓ Claims table updated")
        except Exception as e:
            print(f"Note: {e}")
        
        print("Adding new columns to claim_documents table...")
        try:
            connection.execute(text("""
                ALTER TABLE claim_documents
                ADD COLUMN IF NOT EXISTS cleaned_text TEXT,
                ADD COLUMN IF NOT EXISTS ocr_reviewed_by VARCHAR(255),
                ADD COLUMN IF NOT EXISTS ocr_reviewed_at TIMESTAMP,
                ADD COLUMN IF NOT EXISTS anon_reviewed_by VARCHAR(255),
                ADD COLUMN IF NOT EXISTS anon_reviewed_at TIMESTAMP
            """))
            connection.commit()
            print("✓ Claim documents table updated")
        except Exception as e:
            print(f"Note: {e}")
    
    # Create all new tables
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ All tables created/updated")
    
    print("\n✅ Database migrations completed successfully!")
    print("\nNew tables created:")
    print("  - rag_documents")
    print("  - audit_logs")
    print("  - analysis_reports")
    print("\nExisting tables updated:")
    print("  - claims (added: country, analysis_model)")
    print("  - claim_documents (added: cleaned_text, review tracking)")

if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

