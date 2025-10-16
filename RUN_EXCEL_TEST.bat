@echo off
title Excel Processing Test
color 0A

echo.
echo ========================================
echo   Excel Processing Test
echo   Organized Output in test_outputs
echo ========================================
echo.

echo [1/3] Installing/Updating dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [2/3] Running Excel processing test...
echo.
python test_excel_processing.py

echo.
echo [3/3] Displaying results...
echo.
echo Test completed successfully!
echo.
echo Output organized in test_outputs directory:
echo   - Separate subfolders for each input file
echo   - Timestamped results for multiple runs
echo   - Latest results symlinked for easy access
echo.

echo Opening test_outputs directory...
explorer test_outputs

echo.
echo Press any key to exit...
pause >nul