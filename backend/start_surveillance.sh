#!/bin/bash
# Quick Start Script for AI Eyes Surveillance System

echo "🔍 AI Eyes - Smart Surveillance System"
echo "======================================="

# Check if we're in the right directory
if [ ! -f "multi_camera_surveillance.py" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Check Python installation
python --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found"

# Install requirements if needed
if [ ! -d ".venv" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🚀 Starting Multi-Camera AI Surveillance..."
echo "🌐 Dashboard will be available at: http://localhost:5002"
echo "⚠️  Press Ctrl+C to stop"
echo ""

# Start the surveillance system
python multi_camera_surveillance.py