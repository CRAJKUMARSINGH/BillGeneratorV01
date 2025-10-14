@echo off
echo Starting Bill Generator Application...
echo ====================================

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start the Streamlit application
echo Starting Streamlit application on port 8503...
echo You can access the application at: http://localhost:8503
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.port 8503

pause