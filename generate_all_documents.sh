#!/bin/bash

# Document Generator - All Formats
# Generates HTML, PDF, DOC files

echo ""
echo "========================================"
echo "  Document Generator - All Formats"
echo "  Generates HTML, PDF, DOC files"
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

echo "[1/3] Installing/Updating dependencies..."
if ! $PYTHON_CMD -m pip install -r requirements.txt --quiet; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[2/3] Installing Playwright browsers..."
$PYTHON_CMD -m playwright install-deps > /dev/null 2>&1
$PYTHON_CMD -m playwright install > /dev/null 2>&1

echo "[3/3] Generating all document formats..."
echo ""
$PYTHON_CMD generate_all_documents.py

echo ""
echo "Documents generated successfully!"
echo "Check the 'output' folder for HTML, PDF, and DOC files"
echo ""

# Check if xdg-open or open is available for opening the folder
if command_exists xdg-open; then
    echo "Opening output folder..."
    xdg-open output
elif command_exists open; then
    echo "Opening output folder..."
    open output
fi