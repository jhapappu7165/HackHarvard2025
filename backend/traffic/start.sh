#!/bin/bash
# Boston Daddy Traffic Backend - Quick Start Script

echo "🏙️  Boston Daddy Traffic Backend"
echo "=================================="

# Kill any existing processes and clear ports
echo "🧹 Cleaning up existing processes..."
pkill -f "python run.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "fastapi" 2>/dev/null || true

# Kill any process using port 8000
echo "🔌 Freeing up port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 2

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env file..."
    echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
    echo "✅ Please edit .env file with your actual Gemini API key"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --upgrade
echo "✅ Dependencies installed"

# Verify port 8000 is free
echo "🔍 Verifying port 8000 is available..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8000 is still in use. Please manually kill the process or wait."
    exit 1
else
    echo "✅ Port 8000 is available"
fi

# Run the server
echo "🚀 Starting Boston Daddy Traffic Backend..."
python run.py
