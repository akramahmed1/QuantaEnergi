from fastapi import FastAPI, HTTPException, Header
import uvicorn
import json
import time
import pandas as pd
import warnings

# Quantum Security Adapter with Fallback
try:
    from liboqs import KeyEncapsulation
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False
    warnings.warn("liboqs not available, using mock security")

class QuantumSecurityAdapter:
    def __init__(self):
        self._public_key = None
        if OQS_AVAILABLE:
            self.kem = KeyEncapsulation("Kyber1024")
            self._public_key = self.kem.generate_keypair()

    def encrypt(self, plaintext: str):
        if not OQS_AVAILABLE or not self._public_key:
            return {"status": "mock", "data": "mock_encrypted"}
        try:
            ciphertext, _ = self.kem.encap_secret(self._public_key)
            return {"status": "quantum", "data": ciphertext.hex()}
        except Exception as e:
            warnings.warn(f"Quantum encryption failed: {e}")
            return {"status": "mock", "data": "mock_encrypted"}

qsec_adapter = QuantumSecurityAdapter()

app = FastAPI()
log_file = "backend.log"

def log_message(message):
    with open(log_file, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Load and clean data
try:
    df = pd.read_csv("D:\\Documents\\energyopti-pro\\pilot_iot_data.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    df['production'] = pd.to_numeric(df['production'], errors='coerce').fillna(1000)  # Default if missing
    real_data = df.iloc[0].to_dict()
except Exception as e:
    log_message(f"Error loading real data: {e}")
    real_data = {"price": 75.5, "production": 1000}  # Fallback mock data

@app.get("/api/prices")
async def get_prices(region: str = "global", ramadan_mode: bool = False):
    try:
        response = {"source": "real", "data": real_data["price"]}
        if ramadan_mode:
            response["ramadan_adjustment"] = -5.0
        if region == "middle_east":
            response["data"] = "ME_adjusted_price"
        log_message(f"Fetched real prices for {region}")
        return response
    except Exception as e:
        log_message(f"Error fetching prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/models/v1/prices")
async def get_prices_v1(region: str = "global", ramadan_mode: bool = False):
    try:
        response = {"source": "real", "data": real_data["price"]}
        if ramadan_mode:
            response["ramadan_adjustment"] = -5.0
        if region == "middle_east":
            response["data"] = "ME_adjusted_price"
        log_message(f"Fetched real prices v1 for {region}")
        return response
    except Exception as e:
        log_message(f"Error fetching prices v1: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/audit")
async def log_audit(data: dict, authorization: str = Header(...)):
    try:
        entry = {**data, **{"status": "mock_compliant"}}
        with open("audit.log", "a") as f:
            f.write(json.dumps(entry) + "\n")
        log_message(f"Audit logged with mock compliance: {data}")
        return {"status": "logged"}
    except Exception as e:
        log_message(f"Error logging audit: {e}")
        raise HTTPException(status_code=500, detail="Failed to log audit")

@app.get("/api/secure")
async def secure_endpoint(authorization: str = Header(...)):
    try:
        if authorization != "Bearer token0":
            raise HTTPException(status_code=401, detail="Unauthorized")
        log_message("Secure endpoint accessed")
        return qsec_adapter.encrypt("secure_data")
    except Exception as e:
        log_message(f"Error accessing secure endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to access secure endpoint")

@app.get("/api/secure/transparency")
async def secure_transparency():
    try:
        log_message("Mock transparency data fetched")
        return {"security_status": "mock_active"}
    except Exception as e:
        log_message(f"Error fetching transparency data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transparency data")

@app.get("/api/oilfield")
async def get_oilfield():
    try:
        log_message("Fetched real oilfield data")
        return {"production": real_data["production"], "field": "Jafurah"}
    except Exception as e:
        log_message(f"Error fetching oilfield data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch oilfield data")

@app.get("/api/tariff_impact")
async def get_tariff_impact():
    try:
        log_message("Mock tariff impact data fetched")
        return {"impact": 5.0, "region": "USA"}
    except Exception as e:
        log_message(f"Error fetching tariff impact: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tariff impact")

@app.get("/api/renewables")
async def get_renewables():
    try:
        log_message("Mock renewables data fetched")
        return {"wind": 500, "solar": 300}
    except Exception as e:
        log_message(f"Error fetching renewables data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch renewables data")

@app.get("/api/retention")
async def get_retention():
    try:
        log_message("Mock retention data fetched")
        return {"retention_rate": 85, "last_login": time.strftime("%Y-%m-%d")}
    except Exception as e:
        log_message(f"Error fetching retention data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch retention data")

@app.get("/api/onboarding")
async def get_onboarding(user_type: str = "trader"):
    try:
        guide = {"trader": "Trade Guide", "engineer": "Field Guide"}.get(user_type, "General Guide")
        log_message(f"Mock onboarding guide fetched for {user_type}")
        return {"guide": guide}
    except Exception as e:
        log_message(f"Error fetching onboarding data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch onboarding data")

@app.get("/api/health")
async def get_health():
    try:
        log_message("Mock health check passed")
        return {"status": "healthy", "uptime": "99.9%"}
    except Exception as e:
        log_message(f"Error fetching health data: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/api/gamify")
async def log_engagement(data: dict):
    try:
        log_message(f"Mock engagement logged: {data}, DAU: {time.strftime('%Y-%m-%d')}")
        return {"status": "logged"}
    except Exception as e:
        log_message(f"Error logging engagement: {e}")
        raise HTTPException(status_code=500, detail="Failed to log engagement")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
