#!/bin/bash

# Quick Start Script for Mobile Phone Price Prediction API

echo "🚀 Mobile Phone Price Prediction API - Quick Start"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To start the server, run:"
echo "   python -m app.main"
echo ""
echo "Or:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
