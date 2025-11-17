#!/usr/bin/env pwsh
# Docker Build Test Script for Windows PowerShell

Write-Host "🐳 SmartPLC AI Agent - Docker Build Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found! Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if Docker daemon is running
Write-Host ""
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker daemon is not running! Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Build the Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first build..." -ForegroundColor Gray
Write-Host ""

$buildStart = Get-Date

try {
    docker build -t smartplc-ai-agent:test .
    
    $buildEnd = Get-Date
    $buildDuration = $buildEnd - $buildStart
    
    Write-Host ""
    Write-Host "✓ Docker image built successfully!" -ForegroundColor Green
    Write-Host "  Build time: $($buildDuration.TotalSeconds) seconds" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "✗ Docker build failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

# Show image info
Write-Host ""
Write-Host "Docker image information:" -ForegroundColor Yellow
docker images smartplc-ai-agent:test

# Ask if user wants to run the container
Write-Host ""
$runContainer = Read-Host "Do you want to test run the container? (y/n)"

if ($runContainer -eq 'y' -or $runContainer -eq 'Y') {
    Write-Host ""
    Write-Host "Starting test container..." -ForegroundColor Yellow
    Write-Host "Container will run in detached mode." -ForegroundColor Gray
    Write-Host ""
    
    # Check if .env file exists
    if (Test-Path ".env") {
        Write-Host "✓ Found .env file" -ForegroundColor Green
    } else {
        Write-Host "⚠ No .env file found! Using default configuration." -ForegroundColor Yellow
        Write-Host "  Create a .env file with OPENAI_API_KEY for full functionality." -ForegroundColor Gray
    }
    
    Write-Host ""
    
    # Create data directories if they don't exist
    $dataDirs = @("data/db", "data/logs", "data/exports", "data/vector_store")
    foreach ($dir in $dataDirs) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "✓ Created directory: $dir" -ForegroundColor Green
        }
    }
    
    # Run the container
    try {
        docker run -d `
            --name smartplc-test `
            -e QT_QPA_PLATFORM=offscreen `
            -v "${PWD}/data:/app/data" `
            smartplc-ai-agent:test
        
        Write-Host ""
        Write-Host "✓ Container started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Container name: smartplc-test" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Useful commands:" -ForegroundColor Yellow
        Write-Host "  View logs:     docker logs -f smartplc-test" -ForegroundColor Gray
        Write-Host "  Stop:          docker stop smartplc-test" -ForegroundColor Gray
        Write-Host "  Remove:        docker rm -f smartplc-test" -ForegroundColor Gray
        Write-Host "  Shell access:  docker exec -it smartplc-test /bin/bash" -ForegroundColor Gray
        
        Write-Host ""
        Write-Host "Showing container logs (Ctrl+C to exit)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        docker logs -f smartplc-test
        
    } catch {
        Write-Host ""
        Write-Host "✗ Failed to start container!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "To run the container later, use:" -ForegroundColor Yellow
    Write-Host "  docker run -d --name smartplc smartplc-ai-agent:test" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Done! 🎉" -ForegroundColor Green
