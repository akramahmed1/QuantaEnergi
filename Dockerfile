FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY alembic.ini .
COPY alembic/ ./alembic/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check - fixed endpoint to match the actual health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["gunicorn", "src.energyopti_pro.main:app", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4"]
