#!/bin/bash

# Quick Start Script for Mobile Phone Price Prediction

echo "🚀 Mobile Phone Price Prediction - Quick Start"
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

# Disable __pycache__ generation for this session
export PYTHONDONTWRITEBYTECODE=1

echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To start localhost web UI, run:"
echo "   python app.py"
echo ""
echo "Or train directly:"
echo "   python train.py --records 1000"
echo ""
echo "✅ System now runs on localhost web UI (no API layer)."
echo ""
