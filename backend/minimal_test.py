from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/test")
def test():
    assert True
    # Test passes without return value

if __name__ == "__main__":
    print("Starting minimal test server on port 8080...")
    uvicorn.run(app, host="127.0.0.1", port=8080)
