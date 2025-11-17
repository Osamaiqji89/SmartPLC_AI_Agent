# SmartPLC AI Agent - Multi-Stage Docker Build
# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Qt/PySide6
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxrender1 \
    libxi6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

WORKDIR /tmp

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
# Split into multiple RUN commands for better layer caching and error visibility
RUN pip install --upgrade pip setuptools wheel

# Install core dependencies first
RUN pip install --no-cache-dir \
        PySide6>=6.6.0 \
        openai>=1.0.0 \
        sqlalchemy>=2.0.0 \
        loguru>=0.7.0 \
        python-dotenv>=1.0.0

# Install additional dependencies
RUN pip install --no-cache-dir \
        httpx \
        faiss-cpu \
        sentence-transformers \
        tiktoken \
        pypdf \
        python-docx \
        markdown \
        alembic \
        matplotlib \
        pyqtgraph \
        pydantic \
        pydantic-settings \
        numpy \
        pandas

# Stage 3: Application
FROM base as application

# Create non-root user for security
RUN useradd -m -u 1000 smartplc && \
    mkdir -p /app && \
    chown -R smartplc:smartplc /app

WORKDIR /app

# Copy Python dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=smartplc:smartplc . .

# Create necessary directories
RUN mkdir -p data/db data/logs data/exports data/vector_store && \
    chown -R smartplc:smartplc data/

# Switch to non-root user
USER smartplc

# Initialize knowledge base if script exists
RUN if [ -f "scripts/init_knowledge_base.py" ]; then \
        python scripts/init_knowledge_base.py; \
    fi

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port for potential web interface
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["python"]

# Default command
CMD ["main.py"]
