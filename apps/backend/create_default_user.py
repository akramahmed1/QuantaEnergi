#!/usr/bin/env python3
"""
Create default user for QuantaEnergi ETRM application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, create_tables
from app.models import User
from app.core.auth import auth_manager

def create_default_user():
    """Create default admin user for testing"""
    # Create tables first
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        hashed_password = auth_manager.hash_password("admin123")
        
        admin_user = User(
            username="admin",
            email="admin@quantaenergi.com",
            hashed_password=hashed_password,
            role="admin",
            is_active=True,
            company_name="QuantaEnergi",
            organization_id="default"
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Default admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: admin")
        
    except Exception as e:
        print(f"❌ Error creating default user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_user()
