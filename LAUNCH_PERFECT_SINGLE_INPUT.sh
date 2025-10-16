#!/bin/bash

# Perfect Single Input Bill Generator
# OPTIMIZED FOR SINGLE FILE PROCESSING
# By: RAJKUMAR SINGH CHAUHAN

echo ""
echo "========================================"
echo "  Perfect Single Input Bill Generator"
echo "  OPTIMIZED FOR SINGLE FILE PROCESSING"
echo "  By: RAJKUMAR SINGH CHAUHAN"
echo "========================================"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3 && ! command_exists python; then
    echo "ERROR: Python is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Use python3 if available, otherwise use python
if command_exists python3; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "[1/4] Installing/Updating dependencies..."
if ! $PYTHON_CMD -m pip install -r requirements.txt --quiet; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[2/4] Installing Playwright browsers..."
$PYTHON_CMD -m playwright install-deps > /dev/null 2>&1
$PYTHON_CMD -m playwright install > /dev/null 2>&1

echo "[3/4] Starting Perfect Single Input Application..."
echo ""
echo "========================================"
echo "  Application Starting..."
echo "  Please wait for browser to open..."
echo "========================================"
echo ""

echo "Starting Streamlit application on port 8506..."
$PYTHON_CMD -m streamlit run perfect_single_input_app.py --server.port=8506 --server.address=localhost

echo ""
echo "Application closed."