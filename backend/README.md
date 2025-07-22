# EnergyOpti-Pro Backend

A backend application for energy optimization using FastAPI and gRPC.

## Setup
1. Clone the repository.
2. Create a virtual environment: python -m venv venv
3. Activate it: env\Scripts\Activate.ps1
4. Install dependencies: pip install uvicorn gunicorn redis grpcio pandas requests planet
5. Run FastAPI: uvicorn main:app --host 0.0.0.0 --port 8000
6. Run gRPC: Start-Process -FilePath "python" -ArgumentList "energy_service.py" -NoNewWindow

## APIs
- /api/prices: Get mock price data
- /api/audit: Log audit data
- /api/trade: Submit trade data
- /api/secure: Authenticated endpoint
- /api/demo-credentials: Get demo credentials
- /api/etl: Mock ETL data
- /api/satellite: Mock satellite data

## gRPC
- Service: StreamEnergyData returns prices 75.0 to 79.0
- Client: 	ests/test_grpc.py

## Testing
- Run python tests/test_api.py
- Run python tests/test_grpc.py

## Next Steps
- Integrate real CME Group and Planet APIs.
- Deploy using Docker or Heroku.
- Add a frontend with React.
