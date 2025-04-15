@echo off
echo Starting Network Security AI Platform...
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    goto :end
)

REM Check if required packages are installed
echo Checking required packages...
pip install -q fastapi uvicorn jinja2 python-dotenv google-generativeai pandas numpy

REM Run the application
echo.
echo Starting the application...
echo Access the dashboard at http://localhost:8000
echo.
python enhanced_app.py

:end
pause
