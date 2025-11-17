#!/usr/bin/env bash
# Docker run script for SmartPLC AI Agent

set -e

echo "=========================================="
echo " SmartPLC AI Agent - Docker Setup"
echo "=========================================="
echo ""

# Change to project root
cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    if [ -f config/.env.example ]; then
        cp config/.env.example .env
    fi
    echo ""
    echo "❌ Please edit .env and add your OpenAI API key, then run this script again."
    echo "   File location: $(pwd)/.env"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "sk-your-api-key-here" .env; then
    echo "⚠️  OpenAI API key not configured in .env"
    echo "Please edit .env and add your real API key."
    exit 1
fi

echo "✅ Configuration OK"
echo ""

# Build Docker image
echo "[1/3] Building Docker image..."
docker-compose -f .docker/docker-compose.yml build

echo ""
echo "[2/3] Initializing knowledge base..."
docker-compose -f .docker/docker-compose.yml run --rm plc-studio python scripts/init_knowledge_base.py

echo ""
echo "[3/3] Starting application..."
docker-compose -f .docker/docker-compose.yml up -d

echo ""
echo "=========================================="
echo " ✅ SmartPLC AI Agent Started!"
echo "=========================================="
echo ""
echo "📊 View logs:    docker-compose -f .docker/docker-compose.yml logs -f plc-studio"
echo "⏸️  Stop:         docker-compose -f .docker/docker-compose.yml down"
echo "🔄 Restart:      docker-compose -f .docker/docker-compose.yml restart"
echo ""
