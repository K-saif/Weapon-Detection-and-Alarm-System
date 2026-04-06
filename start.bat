@echo off
REM Quick start script for Weapon Detection System

echo.
echo ============================================
echo Weapon Detection System - Quick Start
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install requirements
        pause
        exit /b 1
    )
)

echo.
echo Select how to start:
echo.
echo 1. Start Streamlit Dashboard (Recommended)
echo 2. Start HTML Dashboard
echo 3. Start Detection + Dashboard
echo 4. Start Detection Only (CLI)
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Starting Streamlit Dashboard...
    echo Open: http://localhost:8501
    streamlit run streamlit_app.py
) else if "%choice%"=="2" (
    echo Opening HTML Dashboard in browser...
    start dashboard.html
) else if "%choice%"=="3" (
    echo.
    echo Starting detection pipeline...
    echo In another terminal, run: streamlit run streamlit_app.py
    echo.
    python main.py --source 0
) else if "%choice%"=="4" (
    echo Starting detection pipeline...
    python main.py --source 0
) else (
    echo Exiting...
)

pause
