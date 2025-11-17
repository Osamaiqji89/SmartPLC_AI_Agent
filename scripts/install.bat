@echo off
REM SmartPLC AI Agent - Installation Script
echo ================================================
echo  SmartPLC AI Agent - Installation
echo ================================================
echo.

REM Change to project root directory
cd /d "%~dp0\.."

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)
python --version
echo.

echo [2/5] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [4/5] Installing dependencies...
echo This may take a few minutes...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

echo [5/5] Setting up configuration...
if not exist ".env" (
    echo Creating .env file from template...
    if exist "config\.env.example" (
        copy config\.env.example .env
    ) else (
        echo WARNING: config\.env.example not found
    )
    echo.
    echo IMPORTANT: Please edit .env and add your OpenAI API key
    echo File location: %CD%\.env
    echo.
) else (
    echo .env file already exists
)
echo.

echo ================================================
echo  Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run: python scripts\init_knowledge_base.py
echo 3. Run: python main.py
echo.
echo Or simply double-click: scripts\start.bat
echo.
pause
