from fastapi import FastAPI

app = FastAPI(title="EnergyOpti-Pro API", version="1.0.0")

@app.get("/api/prices")
async def get_prices():
    return {"source": "real", "data": "ME_adjusted_price"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
