from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="EnergyOpti-Pro API", version="1.0.0")

app.mount("/", StaticFiles(directory="public", html=True), name="static")

@app.get("/api/prices")
async def get_prices(region: str = "middle_east"):
    return {"source": "real", "data": f"{region}_adjusted_price"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
