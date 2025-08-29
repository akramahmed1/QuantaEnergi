#!/bin/bash

# 🚀 EnergyOpti-Pro Quick Start Script
# This script sets up the development environment quickly

set -e

echo "🚀 Starting EnergyOpti-Pro setup..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Dependencies check passed"

# Create environment files
echo "📝 Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    cp env.example backend/.env
    echo "✅ Created backend/.env"
else
    echo "ℹ️  backend/.env already exists"
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env.local
    echo "REACT_APP_ENVIRONMENT=development" >> frontend/.env.local
    echo "✅ Created frontend/.env.local"
else
    echo "ℹ️  frontend/.env.local already exists"
fi

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Run tests
echo "🧪 Running tests..."
cd backend
$PYTHON_CMD -m pytest tests/test_e2e_comprehensive.py -v
cd ..

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Edit frontend/.env.local with your API URL"
echo "3. Start the backend: cd backend && uvicorn app.main:app --reload"
echo "4. Start the frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Service URLs:"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "📚 For more information, see docs/deployment/README.md"
