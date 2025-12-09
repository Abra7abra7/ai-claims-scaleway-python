"""
Script to create initial admin user.
Run after database migration.

Usage:
    python scripts/init_admin.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import User, UserRole
from app.services.auth import hash_password


def create_admin():
    """Create initial admin user if not exists."""
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        
        if admin:
            print(f"✅ Admin user already exists: {admin.email}")
            return
        
        # Get credentials from environment or use defaults
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "admin123456")
        name = os.getenv("ADMIN_NAME", "Admin")
        
        # Create admin user
        admin = User(
            email=email.lower(),
            password_hash=hash_password(password),
            name=name,
            role=UserRole.ADMIN.value,
            locale="sk",
            is_active=True,
            email_verified=True
        )
        
        db.add(admin)
        db.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   ⚠️  Change password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Initializing admin user...")
    create_admin()

