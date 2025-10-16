@echo off
title Perfect Single Input Bill Generator
color 0A

echo.
echo ========================================
echo   Perfect Single Input Bill Generator
echo   OPTIMIZED FOR SINGLE FILE PROCESSING
echo   By: RAJKUMAR SINGH CHAUHAN
echo ========================================
echo.

echo [1/4] Closing previous processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im chrome.exe 2>nul
taskkill /f /im firefox.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/4] Installing/Updating dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/4] Installing Playwright browsers...
playwright install-deps >nul 2>&1
playwright install >nul 2>&1

echo [4/4] Starting Perfect Single Input Application...
echo.
echo ========================================
echo   Application Starting...
echo   Please wait for browser to open...
echo ========================================
echo.

echo Starting Streamlit application on port 8506...
streamlit run perfect_single_input_app.py --server.port=8506 --server.address=localhost

echo.
echo Application closed.
pause