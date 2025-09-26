#!/usr/bin/env python3
"""
Database upgrade script for QuantaEnergi
Runs Alembic migrations to upgrade database schema
"""

import os
import sys
import subprocess
from pathlib import Path

def run_migration():
    """Run database migration using Alembic"""
    
    # Get the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting database migration...")
    print(f"Working directory: {backend_dir}")
    
    try:
        # Check if alembic is available
        result = subprocess.run(['alembic', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Alembic version: {result.stdout.strip()}")
        
        # Check current revision
        result = subprocess.run(['alembic', 'current'], 
                              capture_output=True, text=True, check=True)
        print(f"📊 Current revision: {result.stdout.strip()}")
        
        # Show migration history
        result = subprocess.run(['alembic', 'history', '--verbose'], 
                              capture_output=True, text=True, check=True)
        print(f"📋 Migration history:\n{result.stdout}")
        
        # Run upgrade to head
        print("🔄 Running database upgrade...")
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, check=True)
        print("✅ Database upgrade completed successfully!")
        print(f"Migration output: {result.stdout}")
        
        # Show final revision
        result = subprocess.run(['alembic', 'current'], 
                              capture_output=True, text=True, check=True)
        print(f"📊 Final revision: {result.stdout.strip()}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Alembic not found. Please install it with: pip install alembic")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def check_database_connection():
    """Check if database connection is available"""
    try:
        # Try to import database modules
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure your database is running and connection string is correct")
        return False

if __name__ == "__main__":
    print("🔧 QuantaEnergi Database Migration Tool")
    print("=" * 50)
    
    # Check database connection first
    if not check_database_connection():
        sys.exit(1)
    
    # Run migration
    run_migration()
    
    print("\n🎉 Database migration completed successfully!")
    print("You can now start the application with the updated schema.")
