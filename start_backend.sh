#!/bin/bash
echo "Starting AI Eyes Security System..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start the Flask backend
echo "Starting backend server..."
python app.py
