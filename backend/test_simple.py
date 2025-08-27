from fastapi import FastAPI  # pyright: ignore[reportMissingImports]
import uvicorn  # pyright: ignore[reportMissingImports]

app = FastAPI()

@app.get("/test")
def test():
    return {"message": "Backend is working!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting simple test server on port 8080...")
    uvicorn.run(app, host="127.0.0.1", port=8080)
