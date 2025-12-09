"""
Create auth_tokens table for email verification and password reset.

Run this script to create the auth_tokens table in the database.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()


def create_auth_tokens_table():
    """Create auth_tokens table."""
    engine = create_engine(str(settings.DATABASE_URL))
    
    with engine.connect() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'auth_tokens'
            );
        """))
        
        if result.scalar():
            print("✅ Table 'auth_tokens' already exists")
            return
        
        # Create table
        conn.execute(text("""
            CREATE TABLE auth_tokens (
                id SERIAL PRIMARY KEY,
                token VARCHAR NOT NULL UNIQUE,
                token_type VARCHAR NOT NULL,
                user_email VARCHAR NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX idx_auth_tokens_token ON auth_tokens(token);
            CREATE INDEX idx_auth_tokens_user_email ON auth_tokens(user_email);
            CREATE INDEX idx_auth_tokens_expires_at ON auth_tokens(expires_at);
        """))
        
        conn.commit()
        print("✅ Created table 'auth_tokens' with indexes")


if __name__ == "__main__":
    create_auth_tokens_table()
    print("🎉 Migration complete!")

