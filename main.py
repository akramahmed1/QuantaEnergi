# EnergyOpti-Pro Main Entry Point
# This file imports the actual FastAPI application from the correct module

from src.energyopti_pro.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
