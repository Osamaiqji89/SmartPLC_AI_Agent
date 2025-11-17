@echo off
REM SmartPLC AI Agent - Startup Script
echo ========================================
echo  SmartPLC AI Agent
echo ========================================
echo.

REM Change to project root directory (parent of scripts folder)
cd /d "%~dp0\.."

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file from config/.env.example and add your OpenAI API key
    echo.
    echo Creating .env from template...
    if exist "config\.env.example" (
        copy config\.env.example .env
    ) else (
        echo ERROR: config\.env.example not found
        pause
        exit /b 1
    )
    echo.
    echo Please edit .env and add your OpenAI API key, then restart this script.
    pause
    exit /b 1
)

REM Check if knowledge base is initialized
if not exist "data\vector_store" (
    echo.
    echo Initializing knowledge base...
    python scripts\init_knowledge_base.py
    if errorlevel 1 (
        echo WARNING: Failed to initialize knowledge base
        echo The application will run but AI features may be limited
        pause
    )
)

REM Start application
echo.
echo Starting SmartPLC AI Agent..
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application crashed
    pause
)
