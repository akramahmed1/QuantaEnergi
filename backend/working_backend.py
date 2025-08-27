from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "EnergyOpti-Pro is running"
    })

@app.route('/')
def root():
    return jsonify({
        "message": "EnergyOpti-Pro API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test')
def test():
    return jsonify({
        "message": "API is working!",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    return jsonify({
        "message": "Signup endpoint working",
        "status": "success"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    return jsonify({
        "message": "Login endpoint working",
        "status": "success",
        "token": "test_token_123"
    })

if __name__ == '__main__':
    print("Starting EnergyOpti-Pro Backend on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
