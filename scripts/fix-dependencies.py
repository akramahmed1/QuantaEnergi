#!/usr/bin/env python3
"""
QuantaEnergi Dependency Fix Script
This script fixes the missing dependencies that cause warnings in the backend startup log
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class DependencyFixer:
    """Fix missing dependencies for QuantaEnergi"""
    
    def __init__(self):
        self.project_root = project_root
        self.backend_dir = project_root / "backend"
        self.requirements_file = self.backend_dir / "requirements.txt"
        
    def print_status(self, message, status="INFO"):
        """Print formatted status message"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        print(f"{colors.get(status, colors['INFO'])}[{status}]{colors['RESET']} {message}")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.print_status("Checking Python version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            self.print_status(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "SUCCESS")
            return True
        else:
            self.print_status(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.9+", "ERROR")
            return False
    
    def update_requirements_txt(self):
        """Update requirements.txt with missing dependencies"""
        self.print_status("Updating requirements.txt with missing dependencies...")
        
        try:
            # Read current requirements
            if self.requirements_file.exists():
                with open(self.requirements_file, 'r') as f:
                    current_content = f.read()
            else:
                current_content = ""
            
            # Define missing dependencies
            missing_deps = [
                "# Post-Quantum Cryptography",
                "cryptography[kyber]>=41.0.0",
                "liboqs-python>=0.7.2",
                "",
                "# Quantum Computing",
                "qiskit>=1.0.0",
                "qiskit-aer>=0.12.0",
                "qiskit-algorithms>=0.3.0",
                "qiskit-optimization>=0.5.0",
                "",
                "# Blockchain & Web3",
                "web3>=6.0.0",
                "eth-account>=0.9.0",
                "",
                "# Weather API",
                "requests>=2.31.0",
                "",
                "# Enhanced Security",
                "bandit>=1.7.5",
                "safety>=2.3.0",
                "",
                "# Testing & Development",
                "pytest>=7.4.0",
                "pytest-cov>=4.1.0",
                "pytest-asyncio>=0.21.0",
                "pytest-mock>=3.11.0",
                "httpx>=0.25.0"
            ]
            
            # Check which dependencies are already present
            existing_deps = []
            new_deps = []
            
            for dep in missing_deps:
                if dep.startswith("#") or dep == "":
                    new_deps.append(dep)
                else:
                    dep_name = dep.split(">=")[0].split("==")[0].split("~=")[0]
                    if dep_name in current_content:
                        existing_deps.append(dep)
                    else:
                        new_deps.append(dep)
            
            # Add new dependencies
            if new_deps:
                with open(self.requirements_file, 'a') as f:
                    f.write("\n# QuantaEnergi Enhanced Dependencies\n")
                    for dep in new_deps:
                        f.write(f"{dep}\n")
                
                self.print_status(f"Added {len([d for d in new_deps if not d.startswith('#') and d != ''])} new dependencies", "SUCCESS")
            else:
                self.print_status("All dependencies already present", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.print_status(f"Failed to update requirements.txt: {e}", "ERROR")
            return False
    
    def install_dependencies(self):
        """Install the missing dependencies"""
        self.print_status("Installing missing dependencies...")
        
        try:
            # Change to backend directory
            os.chdir(self.backend_dir)
            
            # Install dependencies
            self.print_status("Installing dependencies from requirements.txt...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_status("Dependencies installed successfully", "SUCCESS")
                return True
            else:
                self.print_status(f"Failed to install dependencies: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.print_status(f"Failed to install dependencies: {e}", "ERROR")
            return False
    
    def create_env_example(self):
        """Create .env.example with required environment variables"""
        self.print_status("Creating .env.example with required environment variables...")
        
        try:
            env_example_file = self.project_root / ".env.example"
            
            env_content = """# QuantaEnergi Environment Configuration
# Copy this file to .env and fill in your values

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/quantaenergi_db
# Alternative: SQLite for development
# DATABASE_URL=sqlite:///./quantaenergi.db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_CLUSTER_NODES=localhost:6379,localhost:6380,localhost:6381

# Blockchain Configuration
INFURA_URL=https://mainnet.infura.io/v3/your_infura_project_id
# Get free API key from: https://infura.io/
# Alternative: Use local simulation
# INFURA_URL=local

# Weather API Configuration
OPENWEATHER_API_KEY=your_openweathermap_api_key
# Get free API key from: https://openweathermap.org/api

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://quantaenergi.vercel.app

# Monitoring Configuration
PROMETHEUS_MULTIPROC_DIR=/tmp
GRAFANA_ADMIN_PASSWORD=quantaenergi_grafana_pass

# Security Configuration
ENCRYPTION_KEY=your-32-character-encryption-key
RATE_LIMIT_PER_MINUTE=100

# Development Configuration
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
"""
            
            with open(env_example_file, 'w') as f:
                f.write(env_content)
            
            self.print_status(".env.example created successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_status(f"Failed to create .env.example: {e}", "ERROR")
            return False
    
    def create_redis_setup_guide(self):
        """Create Redis setup guide"""
        self.print_status("Creating Redis setup guide...")
        
        try:
            redis_guide_file = self.project_root / "docs" / "redis-setup.md"
            redis_guide_file.parent.mkdir(exist_ok=True)
            
            guide_content = """# Redis Setup Guide for QuantaEnergi

## Quick Start (Development)

### Option 1: Docker (Recommended)
```bash
# Start Redis server
docker run -d --name quantaenergi-redis -p 6379:6379 redis:7-alpine

# Check if running
docker ps | grep redis

# Stop Redis
docker stop quantaenergi-redis
```

### Option 2: Local Installation

#### Windows
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Or use WSL2 and follow Linux instructions

#### macOS
```bash
# Using Homebrew
brew install redis
brew services start redis

# Check status
brew services list | grep redis
```

#### Linux (Ubuntu/Debian)
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server
```

## Production Setup

### Redis Cluster (6 nodes)
```bash
# Use the provided docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# This will start:
# - 6 Redis nodes (ports 6379-6384)
# - Redis cluster initialization
# - Redis Commander for management (port 8081)
```

### Health Check
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Test cluster status
redis-cli -p 6379 cluster info
```

## Configuration

### Environment Variables
```bash
# Single Redis instance
REDIS_URL=redis://localhost:6379

# Redis Cluster
REDIS_CLUSTER_NODES=localhost:6379,localhost:6380,localhost:6381,localhost:6382,localhost:6383,localhost:6384
```

### Redis Configuration
The Redis configuration is handled automatically by the Docker setup.
For custom configurations, modify the docker-compose.prod.yml file.

## Troubleshooting

### Common Issues

1. **Connection Refused (Error 10061)**
   - Redis server not running
   - Wrong port number
   - Firewall blocking connection

2. **Redis Cluster Not Initialized**
   - Wait for redis-cluster-init service to complete
   - Check logs: `docker logs quantaenergi-redis-cluster-init`

3. **Memory Issues**
   - Redis default memory limit: 2GB
   - Adjust in docker-compose.prod.yml if needed

### Logs
```bash
# View Redis logs
docker logs quantaenergi-redis-node-1

# View cluster initialization logs
docker logs quantaenergi-redis-cluster-init
```

## Performance Tuning

### Memory Configuration
```yaml
# In docker-compose.prod.yml
redis-node-1:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### Persistence
```yaml
# Data persistence is enabled by default
volumes:
  - redis-data-1:/data
```

## Security

### Network Isolation
- Redis nodes are isolated in the `quantaenergi-network` Docker network
- External access only through Redis Commander (port 8081)

### Authentication
- Redis authentication can be enabled by setting `requirepass` in Redis configuration
- Update environment variables accordingly
"""
            
            with open(redis_guide_file, 'w') as f:
                f.write(guide_content)
            
            self.print_status("Redis setup guide created successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_status(f"Failed to create Redis setup guide: {e}", "ERROR")
            return False
    
    def run_fixes(self):
        """Run all dependency fixes"""
        self.print_status("🔧 Starting QuantaEnergi Dependency Fixes...", "INFO")
        print("=" * 60)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Update requirements.txt
        if not self.update_requirements_txt():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create environment example
        if not self.create_env_example():
            return False
        
        # Create Redis setup guide
        if not self.create_redis_setup_guide():
            return False
        
        self.print_status("All dependency fixes completed successfully!", "SUCCESS")
        return True
    
    def generate_report(self):
        """Generate fix report"""
        print("\n" + "=" * 60)
        self.print_status("📊 Dependency Fix Report", "INFO")
        print("=" * 60)
        
        print(f"\n✅ Fixed Issues:")
        print(f"   - Updated requirements.txt with missing dependencies")
        print(f"   - Installed cryptography[kyber] for post-quantum security")
        print(f"   - Installed Qiskit for quantum computing")
        print(f"   - Installed web3 for blockchain integration")
        print(f"   - Created .env.example with required environment variables")
        print(f"   - Created Redis setup guide")
        
        print(f"\n🔧 Next Steps:")
        print(f"   1. Set up Redis server (see docs/redis-setup.md)")
        print(f"   2. Configure environment variables in .env file")
        print(f"   3. Restart backend server")
        print(f"   4. Verify no warnings in startup log")
        
        print(f"\n🚀 Commands to run:")
        print(f"   # Start Redis (Docker)")
        print(f"   docker run -d --name quantaenergi-redis -p 6379:6379 redis:7-alpine")
        print(f"   ")
        print(f"   # Restart backend")
        print(f"   cd backend && uvicorn app.main:app --reload --port 8000")
        
        return True

def main():
    """Main execution"""
    print("🔧 QuantaEnergi Dependency Fix Script")
    print("=" * 60)
    
    fixer = DependencyFixer()
    
    try:
        # Run all fixes
        success = fixer.run_fixes()
        
        if success:
            # Generate report
            fixer.generate_report()
            sys.exit(0)
        else:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Fix process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
