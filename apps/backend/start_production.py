#!/usr/bin/env python3
"""
QuantaEnergi ETRM/CTRM Production Server
Complete enterprise-grade energy trading platform
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.main import app
from app.core.config import settings

def main():
    """Start the production server"""
    print("🚀 Starting QuantaEnergi ETRM/CTRM Production Server")
    print("=" * 60)
    print("📊 Features Available:")
    print("   • Phase 2: Logistics & Settlement")
    print("   • Phase 3: AI/ML Forecasting & Optimization")
    print("   • Phase 4: Quantum Computing Integration")
    print("   • Phase 5: Billing & Admin Dashboard")
    print("   • 50+ API Endpoints")
    print("   • Multi-Region Compliance")
    print("   • Enterprise-Grade Security")
    print("=" * 60)
    
    # Production server configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
        log_level="info",
        access_log=True,
        server_header=True,
        date_header=True
    )

if __name__ == "__main__":
    main()
