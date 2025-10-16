@echo off
title Document Generator - All Formats
color 0A

echo.
echo ========================================
echo   Document Generator - All Formats
echo   Generates HTML, PDF, DOC files
echo ========================================
echo.

echo [1/3] Installing/Updating dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/3] Installing Playwright browsers...
playwright install-deps >nul 2>&1
playwright install >nul 2>&1

echo [3/3] Generating all document formats...
echo.
python generate_all_documents.py

echo.
echo Documents generated successfully!
echo Check the 'output' folder for HTML, PDF, and DOC files
echo.
echo Press any key to open the output folder...
pause >nul
explorer output