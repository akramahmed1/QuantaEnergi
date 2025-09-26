#!/usr/bin/env python3
"""
QuantaEnergi MVP Startup Script
Starts the FastAPI application with MVP foundations
"""

import uvicorn
import sys
import os

def main():
    """Start the MVP application"""
    print("🚀 Starting QuantaEnergi MVP...")
    print("📍 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("💼 Trade Capture: http://localhost:8000/api/v1/trade/capture")
    print("📊 Risk Management: http://localhost:8000/api/v1/risk/var")
    print("")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down QuantaEnergi MVP...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting MVP: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
