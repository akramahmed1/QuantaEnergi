# Technical Documentation for EnergyOpti-Pro

## API Integration

### Overview
The EnergyOpti-Pro API, hosted at `https://energy-opti-final-1234-6b44b85952ed.herokuapp.com`, provides energy prediction and historical data using a TFLite model and quantum analytics. Built with FastAPI on Heroku.

### Endpoints
- **`/predict` (POST)**: Submits data (e.g., `{"data":[1.0,2.0,3.0]}`) and returns `{"prediction": float}`.
- **`/history` (GET)**: Retrieves `[{"value": float, "timestamp": "datetime"}, ...]`.
- **`/health` (GET)**: Returns `{"status": "healthy"}`.
- **`/terms` (GET)**: Displays terms of service (HTML).
- **`/privacy` (GET)**: Displays privacy policy (HTML).
- **`/quantum` (GET)**: Returns `{"quantum_circuit": str}`.
- **`/backup_db` (GET)**: Triggers S3 backup, returns `{"status": "backup completed"}`.
- **`/insights` (POST)**: Analyzes text, returns `{"insights": {"polarity": float, "subjectivity": float}}`.

### Credentials Management
- **API Key**: Use Heroku OAuth token (`heroku authorizations:create`). Store in `HEROKU_API_KEY`.
- **Security**: Rate limiting (10/minute), Pydantic validation, Fernet encryption.

### Technical Details
- **Framework**: FastAPI, Uvicorn.
- **Database**: SQLite with encryption.
- **Model**: TFLite for predictions.
- **Dependencies**: `requirements.txt` (e.g., `tflite-runtime`, `numpy`).

### Additional Considerations
- **User Manuals**: Planned, detailing API usage and troubleshooting.
- **Error Handling**: Logs 500 errors (e.g., RMSE issues), future retry logic.
- **Scalability Plans**: Limited by Heroku’s free tier; future AWS scaling.
- **Legal Liability Disclaimers**: Predictions are estimates, not legally binding.

### Legal Relevance
- Complies with GDPR, CCPA, and U.S. FERC laws via encryption.
- Supports audits with `/history` data.
