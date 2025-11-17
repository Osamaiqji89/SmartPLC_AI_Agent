# 🐳 Docker Quick Reference

## Quick Commands

### Build
```bash
docker build -t smartplc-ai-agent:latest .
```

### Run
```bash
# With Docker Compose (recommended)
docker-compose up -d

# Standalone
docker run -d --name smartplc -e OPENAI_API_KEY=your_key smartplc-ai-agent:latest
```

### Management
```bash
# Logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Shell access
docker-compose exec smartplc /bin/bash
```

## Test Script (Windows)
```powershell
.\scripts\test-docker-build.ps1
```

## Configuration

### Required
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional
- `OPENAI_MODEL` - Default: `gpt-3.5-turbo`
- `LOG_LEVEL` - Default: `INFO`

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage production build |
| `docker-compose.yml` | Production deployment |
| `docker-compose.dev.yml` | Development with live reload |
| `.dockerignore` | Files to exclude from build |
| `docs/DOCKER.md` | Full documentation |

## Troubleshooting

### Build fails
```bash
docker build --no-cache -t smartplc-ai-agent:latest .
```

### Container won't start
```bash
docker logs smartplc
```

### GUI not working (Linux)
```bash
xhost +local:docker
export DISPLAY=:0
docker-compose up
```

For detailed instructions, see [docs/DOCKER.md](docs/DOCKER.md)
