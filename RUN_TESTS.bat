@echo off
cls
echo ======================================================
echo 🚀 Bill Generator Comprehensive Testing Suite
echo ======================================================
echo This script will run tests for both Excel Upload Mode 
echo and Online Mode of the Bill Generator application.
echo.
echo Testing will begin in 3 seconds...
echo ======================================================
timeout /t 3 /nobreak >nul

echo.
echo 🏃 Running Online Mode Test...
echo ======================================================
python online_mode_demo.py
echo.
echo ✅ Online Mode Test completed!
echo.
timeout /t 2 /nobreak >nul

echo.
echo 🏃 Running Excel Upload Mode Test...
echo ======================================================
python excel_upload_demo.py
echo.
echo ✅ Excel Upload Mode Test completed!
echo.

echo ======================================================
echo 🎉 All tests completed!
echo.
echo 📁 Check the OUTPUT_FILES directory for results
echo 📝 Review the reports for detailed information
echo ======================================================
echo.
echo Press any key to exit...
pause >nul