# Docker Deployment Guide

## 🐳 Docker Setup für SmartPLC AI Agent

Diese Anleitung beschreibt, wie Sie SmartPLC AI Agent mit Docker ausführen.

## 📋 Voraussetzungen

- Docker Desktop (Windows/Mac) oder Docker Engine (Linux)
- Docker Compose (optional, aber empfohlen)
- Git (zum Klonen des Repositories)

## 🚀 Quick Start

### Option 1: Docker Compose (Empfohlen)

1. **Repository klonen:**
   ```bash
   git clone https://github.com/Osamaiqji89/SmartPLC_AI_Agent.git
   cd SmartPLC_AI_Agent
   ```

2. **Umgebungsvariablen konfigurieren:**
   ```bash
   cp .env.example .env
   # Bearbeiten Sie .env und fügen Sie Ihren OpenAI API Key hinzu
   ```

3. **Container starten:**
   ```bash
   docker-compose up -d
   ```

4. **Logs anzeigen:**
   ```bash
   docker-compose logs -f smartplc
   ```

5. **Container stoppen:**
   ```bash
   docker-compose down
   ```

### Option 2: Standalone Docker

1. **Image bauen:**
   ```bash
   docker build -t smartplc-ai-agent:latest .
   ```

2. **Container starten (Linux mit GUI):**
   ```bash
   docker run -d \
     --name smartplc \
     -e OPENAI_API_KEY=your_api_key_here \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     -v $(pwd)/data:/app/data \
     smartplc-ai-agent:latest
   ```

3. **Container starten (Headless ohne GUI):**
   ```bash
   docker run -d \
     --name smartplc \
     -e OPENAI_API_KEY=your_api_key_here \
     -e QT_QPA_PLATFORM=offscreen \
     -v $(pwd)/data:/app/data \
     smartplc-ai-agent:latest
   ```

## 🔧 Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Standard | Erforderlich |
|----------|-------------|----------|--------------|
| `OPENAI_API_KEY` | OpenAI API Schlüssel | - | Ja |
| `OPENAI_MODEL` | OpenAI Modell | `gpt-3.5-turbo` | Nein |
| `LOG_LEVEL` | Logging-Level | `INFO` | Nein |
| `QT_QPA_PLATFORM` | Qt Platform Abstraction | `xcb` | Nein |

### Volumes

| Host-Pfad | Container-Pfad | Beschreibung |
|-----------|----------------|--------------|
| `./data/db` | `/app/data/db` | SQLite Datenbank |
| `./data/logs` | `/app/data/logs` | Anwendungslogs |
| `./data/exports` | `/app/data/exports` | Exportierte Daten |
| `./data/vector_store` | `/app/data/vector_store` | FAISS Vector Store |
| `./config` | `/app/config` | Konfigurationsdateien |

## 🖥️ GUI Support

### Linux (X11)

```bash
# X11 Zugriff erlauben
xhost +local:docker

# Container mit GUI starten
docker-compose up
```

### Windows/Mac

Für GUI-Unterstützung unter Windows/Mac wird ein X11-Server benötigt:

**Windows:**
- VcXsrv oder Xming installieren
- X11-Server starten
- DISPLAY Variable setzen: `export DISPLAY=host.docker.internal:0`

**Mac:**
- XQuartz installieren
- XQuartz öffnen
- In Preferences → Security: "Allow connections from network clients" aktivieren

## 📊 Container Management

### Container-Status prüfen
```bash
docker-compose ps
```

### Container-Logs
```bash
docker-compose logs -f smartplc
```

### In Container einsteigen
```bash
docker-compose exec smartplc /bin/bash
```

### Container neu starten
```bash
docker-compose restart smartplc
```

### Container und Volumes löschen
```bash
docker-compose down -v
```

## 🔍 Troubleshooting

### Problem: GUI wird nicht angezeigt (Linux)

**Lösung:**
```bash
# X11 Zugriff erlauben
xhost +local:docker

# DISPLAY Variable prüfen
echo $DISPLAY

# Container neu starten
docker-compose restart smartplc
```

### Problem: Berechtigungsfehler bei Volumes

**Lösung:**
```bash
# Verzeichnisse erstellen und Berechtigungen setzen
mkdir -p data/db data/logs data/exports data/vector_store
chmod -R 755 data/
```

### Problem: Container startet nicht

**Lösung:**
```bash
# Logs prüfen
docker-compose logs smartplc

# Container Status
docker-compose ps

# Container neu bauen
docker-compose build --no-cache
docker-compose up -d
```

### Problem: OpenAI API Fehler

**Lösung:**
```bash
# API Key in .env prüfen
cat .env | grep OPENAI_API_KEY

# Container neu starten mit korrektem Key
docker-compose down
docker-compose up -d
```

## 🚢 GitHub Container Registry

### Image von GHCR pullen

```bash
# Login zu GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Image pullen
docker pull ghcr.io/osamaiqji89/smartplc_ai_agent:latest

# Container starten
docker run -d \
  --name smartplc \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  ghcr.io/osamaiqji89/smartplc_ai_agent:latest
```

## 🔒 Sicherheit

- Container läuft als non-root User (UID 1000)
- Sensitive Daten nur über Volumes oder Environment Variables
- API Keys niemals im Image speichern
- `.dockerignore` nutzen um sensible Dateien auszuschließen

## 📈 Ressourcen-Limits

Standard-Limits in docker-compose.yml:
- **CPU**: 2 Cores (Limit), 1 Core (Reservation)
- **Memory**: 2GB (Limit), 1GB (Reservation)

Anpassen in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
    reservations:
      cpus: '2'
      memory: 2G
```

## 🧪 Development

### Development Container

```bash
# Container mit Code-Mounting für Entwicklung
docker-compose -f docker-compose.dev.yml up
```

### Image für verschiedene Plattformen bauen

```bash
# Multi-Platform Build (erfordert buildx)
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t smartplc-ai-agent:latest \
  --push .
```

## 📚 Weitere Ressourcen

- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [GitHub Container Registry](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 🤝 Support

Bei Problemen:
1. Logs prüfen: `docker-compose logs -f`
2. Issue auf GitHub erstellen
3. Community fragen

---

**Hinweis:** Stellen Sie sicher, dass sensible Daten (API Keys, Credentials) niemals in das Docker Image committed werden!
