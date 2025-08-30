#!/bin/bash

# EnergyOpti-Pro Frontend Startup Script
echo "🚀 Starting EnergyOpti-Pro Frontend..."

# Kill any process using port 3000
echo "🔍 Checking port 3000..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is busy. Killing existing process..."
    lsof -ti:3000 | xargs kill -9
    sleep 2
fi

# Navigate to frontend directory
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🌐 Starting development server on port 3000..."
npm run dev
