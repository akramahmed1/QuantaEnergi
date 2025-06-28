from fastapi import FastAPI, Form, HTTPException, Header
from fastapi.staticfiles import StaticFiles
import tensorflow as tf
import numpy as np
from collections import deque
import logging
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
VALID_TOKEN = "a1009144b7a5520439407190f9064793"
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=os.path.join(log_dir, "app.log"), format="%(asctime)s - %(levelname)s - %(message)s - v6")

interpreter = tf.lite.Interpreter(model_path="optimized_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
history = deque(maxlen=5)

@app.get("/health")
async def health_check():
    logging.info("Health check requested")
    return {"status": "healthy"}

@app.get("/")
async def home():
    logging.info("Home page requested")
    return {"message": "Welcome to Energy Opti"}

@app.get("/static/index.html", include_in_schema=False)
async def serve_index():
    logging.info("Static index.html requested")
    return StaticFiles(directory="static").serve("index.html")

@app.post("/predict")
async def predict(value: float = Form(...), authorization: str = Header(None)):
    token = authorization.split(" ")[1] if authorization and authorization.startswith("Bearer ") else "unauth"
    if not authorization or not authorization.startswith("Bearer ") or token != VALID_TOKEN:
        logging.warning("Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        logging.info(f"Predict request received with value={value}")
        input_data = np.array([[value]], dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        prediction = float(interpreter.get_tensor(output_details[0]['index'])[0][0])
        history.append((value, prediction))
        logging.info(f"Prediction successful: {prediction}, history={list(history)}")
        return {"prediction": prediction, "history": list(history)}
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return {"error": "Invalid input", "detail": str(ve)}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"error": "Server error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
