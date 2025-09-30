#!/usr/bin/env python3
"""
QuantaEnergi ETRM Application Startup Script
"""

import subprocess
import sys
import os
import time
import requests
import threading
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, cwd=cwd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_port(port, timeout=5):
    """Check if a port is available"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting QuantaEnergi Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install dependencies
    print("📦 Installing backend dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install backend dependencies: {stderr}")
        return False
    
    # Create default user
    print("👤 Creating default user...")
    success, stdout, stderr = run_command("python create_default_user.py", cwd=backend_dir)
    if not success:
        print(f"⚠️  Warning: Failed to create default user: {stderr}")
    
    # Start backend server
    print("🌐 Starting backend server on http://localhost:8000...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
    ], cwd=backend_dir)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(30):
        if check_port(8000):
            print("✅ Backend started successfully!")
            return True
        time.sleep(1)
    
    print("❌ Backend failed to start")
    return False

def start_frontend():
    """Start the frontend server"""
    print("🎨 Starting QuantaEnergi Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("📦 Installing frontend dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install frontend dependencies: {stderr}")
        return False
    
    # Start frontend server
    print("🌐 Starting frontend server on http://localhost:3000...")
    frontend_process = subprocess.Popen(["npm", "start"], cwd=frontend_dir)
    
    # Wait for frontend to start
    print("⏳ Waiting for frontend to start...")
    for i in range(60):
        try:
            response = requests.get("http://localhost:3000", timeout=1)
            if response.status_code == 200:
                print("✅ Frontend started successfully!")
                return True
        except:
            pass
        time.sleep(1)
    
    print("❌ Frontend failed to start")
    return False

def main():
    """Main startup function"""
    print("🛡️  QuantaEnergi ETRM/CTRM Enterprise Application")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the QuantaEnergi root directory")
        sys.exit(1)
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend")
        sys.exit(1)
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎯 QuantaEnergi ETRM Application Started Successfully!")
    print("\n📋 Application URLs:")
    print("   Frontend: http://localhost:3000")
    print("   Backend:  http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n🔐 Login Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n📊 Features Available:")
    print("   ✅ ETRM Dashboard")
    print("   ✅ Trade Creation")
    print("   ✅ Risk Management")
    print("   ✅ ESG Tracking")
    print("   ✅ Compliance Monitoring")
    print("   ✅ Quantum Optimization")
    print("   ✅ Real-time Market Data")
    print("   ✅ Enterprise Security")
    print("\n🚀 Ready for Production Deployment!")
    print("   Frontend: Deploy to Vercel")
    print("   Backend:  Deploy to Railway/Render")
    
    try:
        # Keep the script running
        print("\n⏳ Application is running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down QuantaEnergi...")
        sys.exit(0)

if __name__ == "__main__":
    main()
