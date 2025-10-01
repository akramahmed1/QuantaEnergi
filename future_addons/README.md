# Future Add-ons for QuantaEnergi (Q1 2026+)

## Overview

This directory contains advanced features that are **de-prioritized** for the 2025 market disruption focus. These features will be re-integrated after initial market validation and based on customer demand.

## De-Prioritized Features

### 1. Quantum Portfolio Optimization
**Location:** `backend/app/domains/quantum/`

**Description:**
- QAOA (Quantum Approximate Optimization Algorithm) portfolio optimization
- Qiskit integration for quantum computing
- Classical PuLP fallback optimization
- Portfolio risk minimization with Sharpe ratio maximization

**Why De-prioritized:**
- Requires specialized quantum hardware or cloud access
- Limited SMB adoption and understanding
- High computational complexity for uncertain advantage
- Not critical for 2025 market pain points (volatility, compliance, ESG)

**Re-integration Timeline:**
- Q1 2026: Evaluate quantum advantage for large portfolios (>50 assets)
- Dependent on: Customer demand, quantum hardware availability
- Target use case: Institutional traders with complex multi-commodity portfolios

**Dependencies:**
```python
qiskit==0.45.0
qiskit-aer==0.12.0
qiskit-algorithms==0.3.0
qiskit-optimization==0.5.0
pulp>=2.7  # Classical fallback
```

---

### 2. Blockchain Carbon NFT Trading
**Location:** `backend/app/domains/blockchain/`

**Description:**
- Carbon NFT creation and verification
- Web3/Ethereum smart contract integration
- Blockchain hash verification for ESG certificates
- NFT portfolio management and trading

**Why De-prioritized:**
- Regulatory uncertainty around blockchain/crypto
- Low enterprise adoption for carbon trading
- High gas fees and complexity
- ESG scoring can be achieved without blockchain

**Re-integration Timeline:**
- Q2 2026: Pilot with specific clients interested in Web3
- Dependent on: Regulatory clarity, customer demand
- Target use case: ESG-focused enterprises requiring immutable carbon records

**Dependencies:**
```python
web3==6.11.3
eth-account==0.9.0
```

---

### 3. IoT Sensor Integration (Future Consideration)
**Status:** Concept only, not yet implemented

**Description:**
- Real-time pipeline monitoring
- IoT sensor data for oil/gas infrastructure
- MQTT integration for sensor streams
- Predictive maintenance alerts

**Why Not Prioritized:**
- Requires hardware partnerships and physical deployment
- Not applicable to software-only ETRM platform
- High complexity and cost
- Better suited for post-product-market-fit expansion

**Re-integration Timeline:**
- Q4 2026 or later
- Dependent on: Hardware partnerships, specific customer requests
- Target use case: Integrated ETRM + asset monitoring for oil majors

**Dependencies:**
```python
asyncio-mqtt==0.16.1
paho-mqtt>=1.6.0
```

---

## How to Re-enable These Features

### Step 1: Install Dependencies
```bash
cd backend
pip install -r future_addons_requirements.txt
```

### Step 2: Uncomment Imports in main.py
```python
# In backend/app/main.py, uncomment:
from app.domains.quantum.routers import router as quantum_router
from app.domains.blockchain.routers import router as blockchain_router

# And uncomment router includes:
app.include_router(quantum_router, prefix="/api/v1")
app.include_router(blockchain_router, prefix="/api/v1")
```

### Step 3: Update Documentation
- Add API endpoints to OpenAPI spec
- Update frontend TypeScript types
- Create user-facing documentation

---

## 2025 Core Focus Areas

Instead of these experimental features, we're focusing on:

✅ **Real-time Risk Analytics** - Monte Carlo VaR, P&L calculations  
✅ **AI Forecasting** - Prophet/XGBoost for price prediction (MAE <5%)  
✅ **Compliance Automation** - REMIT/EMIR validation  
✅ **ESG Scoring** - Carbon footprint without blockchain complexity  
✅ **Market Data Integration** - Alpha Vantage, geo-risk feeds  
✅ **Security** - JWT, audit trails, PQC-ready architecture  

---

## Contact

For questions about re-enabling these features, contact the QuantaEnergi team:
- **Email:** team@quantaenergi.com
- **GitHub:** https://github.com/akramahmed1/QuantaEnergi

---

**Last Updated:** October 1, 2025  
**Next Review:** January 2026 (Post-MVP market validation)

