#!/usr/bin/env python3
"""
QuantaEnergi Warning Fixes Script
Fixes all identified warnings: Kyber/liboqs, Redis, Qiskit, Infura, IoT
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def create_env_file():
    """Create .env file with all required configurations"""
    env_content = """# QuantaEnergi Environment Configuration
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/quantaenergi
POSTGRES_DB=quantaenergi
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ISSUER=quantaenergi
AUDIENCE=quantaenergi-users

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Blockchain (Infura)
INFURA_URL=https://mainnet.infura.io/v3/your_infura_key_here
WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/your_infura_key_here

# IoT & External APIs
OPENWEATHER_API_KEY=your_openweather_key_here
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000", "https://quantaenergi-frontend.vercel.app"]

# Monitoring
PROMETHEUS_MULTIPROC_DIR=/tmp
ENABLE_METRICS=true

# Security
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
ENABLE_HTTPS=true

# Development
DEBUG=true
LOG_LEVEL=INFO
"""
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with all configurations")
    else:
        print("ℹ️ .env file already exists")

def fix_kyber_liboqs():
    """Fix Kyber/liboqs issues"""
    print("\n🔐 Fixing Kyber/liboqs issues...")
    
    # Try to install cryptography with Kyber support
    if run_command("pip install cryptography[kyber] --force-reinstall", "Installing cryptography with Kyber"):
        print("✅ Kyber support installed")
    
    # Try to install liboqs-python
    if run_command("pip install liboqs-python --force-reinstall", "Installing liboqs-python"):
        print("✅ liboqs-python installed")
    
    # Test import
    try:
        import cryptography.hazmat.primitives.kem.kyber
        print("✅ Kyber import successful")
    except ImportError:
        print("⚠️ Kyber import failed - will use fallback security")
    
    try:
        import liboqs
        print("✅ liboqs import successful")
    except ImportError:
        print("⚠️ liboqs import failed - will use fallback security")

def fix_qiskit():
    """Fix Qiskit version conflicts"""
    print("\n⚛️ Fixing Qiskit issues...")
    
    # Uninstall existing Qiskit packages
    run_command("pip uninstall qiskit qiskit-aer qiskit-algorithms qiskit-optimization qiskit-machine-learning -y", "Uninstalling existing Qiskit packages")
    
    # Install compatible versions
    if run_command("pip install qiskit==0.45.0 qiskit-aer==0.12.0 qiskit-algorithms==0.3.0 qiskit-optimization==0.5.0 qiskit-machine-learning==0.5.0", "Installing compatible Qiskit versions"):
        print("✅ Qiskit packages installed with compatible versions")
    
    # Test import
    try:
        import qiskit
        version = getattr(qiskit, '__version__', 'version unknown')
        print(f"✅ Qiskit import successful: {version}")
    except ImportError as e:
        print(f"❌ Qiskit import failed: {e}")

def fix_redis():
    """Fix Redis connection issues"""
    print("\n🔴 Fixing Redis issues...")
    
    # Check if Redis is running
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
        r.ping()
        print("✅ Redis is running and accessible")
    except Exception as e:
        print(f"⚠️ Redis not accessible: {e}")
        print("📋 To fix Redis:")
        print("   1. Download Redis for Windows from: https://github.com/tporadowski/redis/releases")
        print("   2. Run redis-server.exe")
        print("   3. Or use Docker: docker run -d -p 6379:6379 redis:alpine")

def fix_web3():
    """Fix Web3/Infura issues"""
    print("\n⛓️ Fixing Web3/Infura issues...")
    
    # Install/upgrade web3
    if run_command("pip install web3 --upgrade", "Installing/upgrading Web3"):
        print("✅ Web3 installed/upgraded")
    
    # Test import
    try:
        from web3 import Web3
        print("✅ Web3 import successful")
    except ImportError as e:
        print(f"❌ Web3 import failed: {e}")

def fix_other_dependencies():
    """Fix other dependency issues"""
    print("\n🔧 Fixing other dependencies...")
    
    # Install additional required packages
    packages = [
        "structlog",
        "prometheus-client",
        "websockets",
        "celery",
        "python-decouple",
        "httpx",
        "pytest-mock"
    ]
    
    for package in packages:
        run_command(f"pip install {package}", f"Installing {package}")

def create_redis_setup_guide():
    """Create Redis setup guide for Windows"""
    guide_content = """# Redis Setup Guide for Windows

## Option 1: Native Windows Installation (Recommended)
1. Download Redis for Windows from: https://github.com/tporadowski/redis/releases
2. Download the latest `.msi` file
3. Install Redis
4. Start Redis server: `redis-server.exe`
5. Test connection: `redis-cli ping`

## Option 2: WSL2 (Windows Subsystem for Linux)
1. Install WSL2: `wsl --install`
2. Install Redis in WSL: `sudo apt update && sudo apt install redis-server`
3. Start Redis: `sudo service redis-server start`
4. Configure Windows to connect to WSL Redis

## Option 3: Docker (if available)
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

## Option 4: Redis Cloud (Free Tier)
1. Sign up at https://redis.com/try-free/
2. Get connection string
3. Update .env: `REDIS_URL=your_redis_cloud_url`

## Option 5: Skip Redis for Development
If you can't get Redis running, the app will work with caching disabled.
Update .env: `ENABLE_CACHING=false`
"""
    
    guide_path = Path("../docs/windows-redis-setup.md")
    guide_path.parent.mkdir(exist_ok=True)
    
    with open(guide_path, "w") as f:
        f.write(guide_content)
    print("✅ Created Redis setup guide: docs/windows-redis-setup.md")

def main():
    """Main fix function"""
    print("🚀 QuantaEnergi Warning Fixes Script")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Fix all issues
    fix_kyber_liboqs()
    fix_qiskit()
    fix_redis()
    fix_web3()
    fix_other_dependencies()
    
    # Create setup guides
    create_redis_setup_guide()
    
    print("\n" + "=" * 50)
    print("🎉 Warning fixes completed!")
    print("\n📋 Next steps:")
    print("1. Configure your .env file with real API keys")
    print("2. Start Redis server")
    print("3. Test backend: uvicorn app.main:app --reload --port 8000")
    print("\n📚 Check docs/windows-redis-setup.md for Redis setup help")

if __name__ == "__main__":
    main()
