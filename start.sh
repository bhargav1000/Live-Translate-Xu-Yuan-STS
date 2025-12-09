#!/bin/bash

# Live Translate Startup Script

echo "🚀 Starting Live Translate..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if FastAPI is already running on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ FastAPI server already running on port 8000"
else
    echo "📡 Starting FastAPI server..."
    uvicorn fast_api:app --host 0.0.0.0 --port 8000 &
    FASTAPI_PID=$!
    sleep 3
    echo "✅ FastAPI server started (PID: $FASTAPI_PID)"
fi

echo ""
echo "🌐 Opening Live Translate in your browser..."
echo ""
echo "   URL: http://localhost:8000/static/index.html"
echo ""
echo "📝 Instructions:"
echo "   1. Allow microphone access when prompted"
echo "   2. Select source and target languages"
echo "   3. Press and HOLD the button to record"
echo "   4. Release to auto-translate"
echo ""
echo "⚠️  Keep this terminal open while using Live Translate"
echo "   Press Ctrl+C to stop the server"
echo ""

# Open browser (macOS)
if command -v open &> /dev/null; then
    sleep 1
    open "http://localhost:8000/static/index.html"
fi

# Wait for user interrupt
wait
