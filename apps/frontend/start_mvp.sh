#!/bin/bash
# QuantaEnergi Frontend MVP Startup Script

echo "🚀 Starting QuantaEnergi Frontend MVP..."
echo "📍 Frontend: http://localhost:3000"
echo "💼 Trade Capture: http://localhost:3000/trade-capture"
echo "📊 Risk Dashboard: http://localhost:3000/risk-dashboard"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server..."
npm run dev
