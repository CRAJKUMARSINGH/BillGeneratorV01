@echo off
title Infrastructure Billing System - OPTIMIZED VERSION
color 0A

echo.
echo ========================================
echo   Infrastructure Billing System
echo   OPTIMIZED VERSION 3.0
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

echo [3/4] Starting application...
echo.
echo ========================================
echo   Application Starting...
echo   Please wait for browser to open...
echo ========================================
echo.

streamlit run app.py --server.port=8501 --server.address=localhost

echo.
echo Application closed.
pause
