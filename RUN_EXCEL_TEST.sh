#!/bin/bash

# Excel Processing Test
# Organized Output in test_outputs

echo ""
echo "========================================"
echo "  Excel Processing Test"
echo "  Organized Output in test_outputs"
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

echo "[2/3] Running Excel processing test..."
echo ""
$PYTHON_CMD test_excel_processing.py

echo ""
echo "[3/3] Displaying results..."
echo ""
echo "Test completed successfully!"
echo ""
echo "Output organized in test_outputs directory:"
echo "  - Separate subfolders for each input file"
echo "  - Timestamped results for multiple runs"
echo "  - Latest results symlinked for easy access"
echo ""

# Check if xdg-open or open is available for opening the folder
if command_exists xdg-open; then
    echo "Opening test_outputs directory..."
    xdg-open test_outputs
elif command_exists open; then
    echo "Opening test_outputs directory..."
    open test_outputs
fi