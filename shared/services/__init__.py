"""
Services module for EnergyOpti-Pro backend.

This module contains all business logic services including:
- AI/ML Forecasting Service
- Quantum Optimization Service  
- Blockchain Smart Contracts Service
- IoT Integration Service
- Multi-Region Compliance Service
- Generative AI Service
- Billing Service
- Optimization Engine
- Data Integration Service
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from .forecasting_service import forecasting_service
    from .quantum_optimization_service import quantum_optimization_service
    from .blockchain_service import blockchain_service
    from .iot_integration_service import iot_integration_service
    from .compliance_service import compliance_service
    from .generative_ai_service import generative_ai_service
    from .billing_service import billing_service
    from .optimization_engine import optimization_engine
    from .data_integration_service import data_integration_service
except ImportError as e:
    # Fallback if services not available
    print(f"Warning: Some services not available: {e}")
    forecasting_service = None
    quantum_optimization_service = None
    blockchain_service = None
    iot_integration_service = None
    compliance_service = None
    generative_ai_service = None
    billing_service = None
    optimization_engine = None
    data_integration_service = None

__all__ = [
    "forecasting_service",
    "quantum_optimization_service", 
    "blockchain_service",
    "iot_integration_service",
    "compliance_service",
    "generative_ai_service",
    "billing_service",
    "optimization_engine",
    "data_integration_service"
]
