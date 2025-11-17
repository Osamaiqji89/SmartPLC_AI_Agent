@echo off
REM Docker run script for Windows

echo ==========================================
echo  SmartPLC AI Agent - Docker Setup
echo ==========================================
echo.

REM Change to project root
cd /d "%~dp0\.."

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from template...
    if exist "config\.env.example" (
        copy config\.env.example .env
    )
    echo.
    echo Please edit .env and add your OpenAI API key, then run this script again.
    echo File location: %CD%\.env
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/3] Building Docker image...
docker-compose -f .docker\docker-compose.yml build
if errorlevel 1 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

echo.
echo [2/3] Initializing knowledge base...
docker-compose -f .docker\docker-compose.yml run --rm plc-studio python scripts\init_knowledge_base.py

echo.
echo [3/3] Starting application...
docker-compose -f .docker\docker-compose.yml up -d

echo.
echo ==========================================
echo  SmartPLC AI Agent Started!
echo ==========================================
echo.
echo View logs:    docker-compose -f .docker\docker-compose.yml logs -f plc-studio
echo Stop:         docker-compose -f .docker\docker-compose.yml down
echo Restart:      docker-compose -f .docker\docker-compose.yml restart
echo.
pause
