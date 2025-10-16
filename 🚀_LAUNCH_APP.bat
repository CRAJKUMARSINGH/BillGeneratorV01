@echo off
title Bill Generator - OPTIMIZED VERSION
color 0A

echo.
echo ========================================
echo   Bill Generator
echo   OPTIMIZED VERSION 3.0
echo   By: RAJKUMAR SINGH CHAUHAN
echo ========================================
echo.

:menu
echo Select an option:
echo 1. Launch Web Application
echo 2. Generate All Document Formats (PDF, DOC, HTML)
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto launch_app
if "%choice%"=="2" goto generate_docs
if "%choice%"=="3" goto exit_script
echo Invalid choice. Please try again.
echo.
goto menu

:launch_app
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

echo [4/4] Starting application...
echo.
echo ========================================
echo   Application Starting...
echo   Please wait for browser to open...
echo ========================================
echo.

echo Starting Streamlit application on port 8504...
streamlit run app.py --server.port=8504 --server.address=localhost
goto menu

:generate_docs
echo.
echo Generating all document formats...
echo.
call GENERATE_ALL_DOCUMENTS.bat
goto menu

:exit_script
echo.
echo Thank you for using Bill Generator!
echo.
pause
exit /b 0