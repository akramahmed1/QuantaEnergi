from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from app.core.rbac import check_role
from app.db.schemas import User
router = APIRouter()

class QuantumRequest(BaseModel):
    market_data: dict
    strategy: str = "aggressive"

class QuantumResponse(BaseModel):
    status: str
    simulation: dict

@router.post("/simulate", response_model=QuantumResponse)
async def quantum_simulation(request: QuantumRequest, user: User = Depends(check_role("trader"))):
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    if request.strategy == "aggressive":
        qc.rx(np.pi / 2, 0)
    qc.cx(0, 1)
    qc.measure_all()
    sim = AerSimulator()
    result = sim.run(qc, shots=1024).result()
    counts = result.get_counts()
    optimal_allocation = counts.get('00', 0) / 1024 if '00' in counts else 0.5
    scaled_allocation = optimal_allocation * (request.market_data.get("brent_price", 80.0) / 100)
    return {"status": "success", "simulation": {"optimal_allocation": scaled_allocation, "counts": counts}}